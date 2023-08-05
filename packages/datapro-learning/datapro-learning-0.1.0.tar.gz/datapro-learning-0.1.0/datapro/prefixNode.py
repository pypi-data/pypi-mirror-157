
class Node:
  """
  Instantiate a prefix node.
  This will produce prefix tree to find sequence of pattern.

  :param token: The token of this node
  :type token: str

  :param examples: The observations that match with this pattern.
  :type examples: list

  :param pattern: A list of sequcent pattern.
  :type pattern: list

  :param parent_regex: Accumulates the regex of up to this node.
  :type parent_regex: str

  :param next_po: The next position or index that this node will consider.
  :type next_po: str

  :param parent: The parent node.
  :type parent: str
  """

  def __init__(self, token="", examples=[], pattern=[], parent_regex="", next_po="",parent=""):
    self.token = token
    self.examples = examples
    self.count = len(examples)
    self.pattern = pattern
    self.children = []
    self.regex = parent_regex
    self.next_po = next_po
    self.parent = parent

  def info(self):
    print("token:", self.token)
    print("amount of example:", self.count)
    print("pattern:", self.pattern)
    print("next_po:", self.next_po)

  def get_children_token_type(self, tree_type, dict_token, k):
    uniq_token = set()
    for ex in self.examples :
      # bound range
      if len(ex) > self.next_po :
          uniq_token.add(ex[self.next_po])
    
    set_token_type = set()
    for token in uniq_token :
      is_uniq = (dict_token[token] >= k)
      # print(token, dict_token[token], k, is_uniq)
      set_token_type = set_token_type.union(tree_type.assign_type(token, is_uniq))
    return set_token_type
  
  def print_space(self, k) :
    for i in range(len(k)) :
      if k[i][1]:
        print(" ", end="")
      else :
        print("|", end="")
      for j in range(k[i][0]):
        print(" ", end="")

  def display(self, level=0, stack_space=[]):
    cnt = 0
    size = len(self.children)
    for child in self.children :
      self.print_space(stack_space)
      if cnt == size-1 :
        print("└── " + child.token)
      else :
        print("├── " + child.token)
      temp = stack_space.copy()
      temp.append([2 + int(len(child.token)/2), cnt == size-1])
      child.display(level+1, temp)
      cnt+=1
    
  def find(self,name_token) :
    for child in self.children :
      if child.token == name_token : return child
      res = child.find(name_token) 
      if res : return res
    return None