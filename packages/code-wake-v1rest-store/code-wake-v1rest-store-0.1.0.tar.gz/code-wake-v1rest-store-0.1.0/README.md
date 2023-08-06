# Python Code Wake V1 REST API store adapter (pycodewake-v1rest-store)

[![test](https://github.com/mwri/pycodewake-v1rest-store/actions/workflows/test.yml/badge.svg)](https://github.com/mwri/pycodewake-v1rest-store/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/mwri/pycodewake-v1rest-store/branch/main/graph/badge.svg)](https://codecov.io/gh/mwri/pycodewake-v1rest-store)

This store adapter provides backing via the V1 REST API for Code Wake. A server
implementing this API may be achieved by using pycodewake-v1wsgi-service (a middleware
you could use to provide the API via a Flask server say, if that suits.

For example:

```python
import code_wake
from code_wake_v1rest_store import V1RestStore

cwproc = code_wake.Process(
    app_name="my_app",
    app_vsn="1.2.3",
    env_name="production",
    store=V1RestStore("https://code.wake.server/path/to/api"),
)
```
