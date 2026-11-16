"""No dependency required for first half; explore requests after installing it."""
import importlib.util
import json
import sys

print('Python interpreter:', sys.executable)
print('json from:', getattr(json, '__file__', 'built-in'))
print('requests installed?', importlib.util.find_spec('requests') is not None)
print('json tools:', [name for name in dir(json) if name in {'load','loads','dump','dumps'}])
print('Try interactively: help(json.loads)')
