from .prefixNode import Node
from .treeType import TreeOfType

from queue import Queue
from pythainlp import word_tokenize
from scipy.stats import norm
import math
import re

import pandas as pd

class DataPro:
  """
  Instantiate a Data pro model.
  The model will be trained by given data field, alpha and k_percentage.

  :param alpha: The alpha is used to test hypotheses.
  :type alpha: float

  :param k_percentage: The percentage of occuring data proportion with all token.
  :type k_percentage: int
  """
  def __init__(self, alpha=0.05, k_percentage=5):
    self.alpha = alpha
    self.k_percentage = k_percentage
    self.root = Node()
    self.tree_type = TreeOfType()
    self.res = []
    self.data = []
    self.tokenize_data = []
  
  def get_dic_token(self):
    # data is a list of list
    # O(nm) n = amount of data, m = lenght of each data.
    dictT = {}
    cnt = 0
    for row in self.tokenize_data :
      for token in row :
        tokenTs = self.tree_type.assign_type(token, False)
        tokenTs.add(token)
        for tokenT in tokenTs :
          if tokenT not in dictT :
            dictT[tokenT] = 1
          else :
            dictT[tokenT] +=1
        cnt+=1
    return dictT,cnt
  
  def tokenize(self, data):
    s = []
    for x in data :
      s.append(word_tokenize(str(x)))
    return s

  def significant(self, count1, count2, num_token, token_count, alpha):
    """
      param:
        - count1 : count seq that token C appear after seq Q
        - count2 : count seq Q
        - num_token : amount of token C
        - token_count : amount of all token in data field
        - alpha 
    """
    p1 = count1 / count2
    p2 = num_token / token_count # overall prob of occurrence token T 
    p_a = (count1 + num_token) / (count2 + token_count)
    try :
      z = (p1 -p2) / math.sqrt(p_a * (1-p_a) * (1/count2 + 1/token_count))
    except :
      z = 1e9 # case prop = 1
    cdf = norm.cdf(-z, 0, 1) # z-score
    return cdf < alpha

  def load_tree_type(self, path) :
    self.tree_type = self.tree_type.load_tree_type(path)
  
  def fit(self, data) :
    self.data = data
    self.tokenize_data = self.tokenize(data)
    k = int((self.k_percentage/100) * len(self.data)) 

    q = Queue()
    self.root = Node("root", self.tokenize_data, [], "", 0, None)
    q.put(self.root)


    # Knowing how many token occuring in the data before assigned type.
    # ** token_count required before all seq token's type are generated. Actualy token
    dict_token, token_count = self.get_dic_token()

    while not q.empty():
        # node Q
        Q = q.get()

        # Create children Of Q 
        # Get all posible token that are children of Q
        all_token_type = Q.get_children_token_type(self.tree_type, dict_token, k)
        for tokenT in all_token_type :
          C = Node(tokenT, [], Q.pattern.copy(), Q.regex ,Q.next_po+1, Q)
          C.examples = [ex for ex in Q.examples if (Q.next_po < len(ex) and self.tree_type.follow_by(ex[Q.next_po],tokenT))]
          C.count = len(C.examples)
          C.pattern.append(tokenT)
          C.regex += self.tree_type.unfix_format(self.tree_type.tree_type[tokenT]["regex"])
          if self.significant(C.count, Q.count, dict_token[tokenT], token_count, self.alpha) :
            Q.children.append(C)
        
        # Prune gerneralizations ?
        temp_children = []
        for C in Q.children :
          N = C.count
          for S in Q.children :
            if S.token != C.token and self.tree_type.sub_generalize(S.token, C.token):
              N -= S.count
          if self.significant(N, Q.count, dict_token[C.token], token_count, self.alpha) :
            temp_children.append(C)
            q.put(C)
        Q.children = temp_children

        # Determinize children of Q
        for C in Q.children :
          for S in Q.children :
            if S.token != C.token and self.tree_type.sub_generalize(S.token, C.token) :
              new_examples = []
              for x in C.examples :
                if x not in S.examples :
                  new_examples.append(x)
              C.examples = new_examples
          C.count = len(C.examples)

    # Extract patterns from tree
    self.res = []
    q = Queue()
    q.put(self.root)
    while not q.empty() :
      Q = q.get()
      for C in Q.children :
        N = C.count
        q.put(C)
        for S in C.children :
            N-=S.count
        if self.significant(N, Q.count, dict_token[C.token], token_count, self.alpha) :
          self.res.append(C.pattern)

  """
  Method for seeing the result.
  """

  def display_tree_type(self):
    self.tree_type.display()

  def display(self):
    self.root.display()
  
  def result(self):
    return self.res
  
  def evaluate_score(self) :
    def measure_matching(pattern) :
      '''
      This function compares the pattern with seq_token_data which is generated after tokenize.
      '''
      cnt = 0;
      size_pattern = len(pattern)
      for data in self.tokenize_data :
        if size_pattern == len(data) :
          is_match = True
          for token_i in range(size_pattern) :
            if not re.search(self.tree_type.tree_type[pattern[token_i]]["regex"], data[token_i]):
              is_match = False
              break
          if is_match: cnt+=1
      return cnt/len(self.tokenize_data)
    res_df = pd.DataFrame(columns=["pattern", "score"])
    res_df["pattern"] = self.res
    res_df["score"] = res_df["pattern"].apply(lambda x: measure_matching(x))
    res_df = res_df.sort_values(by=["score"], ascending=False).reset_index()
    res_df.drop("index", axis=1, inplace=True)
    return res_df