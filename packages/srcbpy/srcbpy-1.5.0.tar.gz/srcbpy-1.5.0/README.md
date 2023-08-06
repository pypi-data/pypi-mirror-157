# srcbpy
A simple api wrapper for (pastebin) sourceb.in.

# Installation
```
pip install srcbpy
```

# Usage
```py
from srcbpy import srcb
api = srcb()
print(srcb.paste('file_path')) # You don't need to do open file code, just type the file path and it will automatically read it.
```