# A company manages servers across multiple environments. 
# We need to examine an inventory and identify servers that violate operational requirements.

#!/usr/bin/env python3
"""Audit an inventory snapshot. Exit 2 means policy violations were found."""
import argparse
from collections import Counter, defaultdict # Counter(['a', 'b', 'a']) gives {'a': 2, 'b': 1}).
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # python_for_devops_class2/


raw_data = json.loads(Path("data/inventory.json").read_text())
print(type(raw_data))


final_data = json.dumps(raw_data)
print(type(final_data))   # <class 'str'>