# DataPro algorithm

The task is learning the common structure of data. The DataPro algorithm is the algorithm that finds statistically significant patterns in a set of token sequences.
This repository is Implemented from the paper "Learning the Common Structure of Data" by Kristina Lerman and Steven Minton.

## installation

```console
pip install learn-structure-datapro
```

## Get started

How to use model with this lib:

```python
from datapro import DataPro
import pandas as pd

# Read data file
df = pd.read_excel("street_road.xlsx")
df = df.dropna()

# Choose a column.
data_sample = df["หน่วยรับผิดชอบ"]

# Create datapro object.
s = DataPro(alpha=0.05, k_percentage=10)

# Train with data
s.fit(data_sample)

# show result
print(s.evaluate_score())
```

# Reference

https://www.aaai.org/Papers/AAAI/2000/AAAI00-093.pdf
