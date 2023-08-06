# pe-accounting-python-api

Python package to use the PE Accounting API with Python.

PE Accounting is the Swedish bookkeeping system found at <https://www.accounting.pe/sv/var-tjanst>. PE's API docs are here: <https://api-doc.accounting.pe>.

```sh
pip install pe-accounting-python-api
```

```python
from pe_accounting_python_api import RESTCLIENT
pe = RESTCLIENT(token=123123)
```
