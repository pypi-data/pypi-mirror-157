# DEEP_causal

DEEP_causal is a Python library for discovering causal heterogeneity. The mechanism can be found in the publication "Causal heterogeneity discovery by bottom-up pattern search".

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install DEEP_causal.

```bash 
pip install DEEP_causal
```

## Usage

```python
from DEEP_causal import compute_DEEP_causal
import pandas as pd

# read example training data and testing data
# example data is available at https://drive.google.com/drive/folders/1UW_bcZ7d_ygTXRjJlfR4JrvFKJwWq30D
train_data = pd.read_csv("example_train.csv")
test_data = pd.read_csv("example_test.csv")

# parents, treatment, outcome
parents_trtout = ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "w", "y"]   # from MMPC

# returns patterns and causal effect
train_output, test_output = compute_DEEP_causal.compute_dc(train_data, parents_trtout, test_data)

```