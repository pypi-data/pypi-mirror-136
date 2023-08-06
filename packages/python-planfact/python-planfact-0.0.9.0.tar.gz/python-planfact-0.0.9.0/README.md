# Simple python wrapper for planfact.io API

### Resource

planfact API documentation: https://apidoc.planfact.io

### Installation

```pip install python-planfact```

### Example usage:

```python
import os
import planfact_api as pf

os.environ["PF_API_KEY"] = "YOUR_API_KEY_HERE"
currencies = pf.get_currencies()
```
