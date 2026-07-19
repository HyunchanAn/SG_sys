# Repository E2E & Consistency Test Report
Date: Sun Jul 19 11:22:55 KST 2026

## SG_sys
No tests found.

## SG_DB
No tests found.

## SG_proj_001
```text
============================= test session starts ==============================
platform linux -- Python 3.10.20, pytest-9.1.1, pluggy-1.6.0
rootdir: /app/SG_proj_001
configfile: pyproject.toml
plugins: asyncio-1.4.0, anyio-4.14.2
asyncio: mode=strict, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 3 items

tests/test_engine.py ...                                                 [100%]

=============================== warnings summary ===============================
tests/test_engine.py::test_recipe_optimizer_init
  /usr/local/lib/python3.10/site-packages/sklearn/base.py:442: InconsistentVersionWarning: Trying to unpickle estimator KMeans from version 1.8.0 when using version 1.7.2. This might lead to breaking code or invalid results. Use at your own risk. For more info please refer to:
  https://scikit-learn.org/stable/model_persistence.html#security-maintainability-limitations
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================= 3 passed, 1 warning in 1.10s =========================
```
**Status: PASSED :white_check_mark:**

## SG_proj_002
```text
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-9.0.3, pluggy-1.5.0
rootdir: /Users/hyunchanan/Documents/GitHub/SG_proj_002
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.1.0, hypothesis-6.155.7, hydra-core-1.3.2, respx-0.23.1
collected 14 items / 1 error

==================================== ERRORS ====================================
______________________ ERROR collecting tests/test_api.py ______________________
ImportError while importing test module '/Users/hyunchanan/Documents/GitHub/SG_proj_002/tests/test_api.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Caskroom/miniconda/base/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_api.py:8: in <module>
    from api.main import app
api/main.py:9: in <module>
    from .routers import analysis
api/routers/analysis.py:7: in <module>
    from ..schemas import (
api/schemas.py:1: in <module>
    from shared_schemas.p002_sfe import *
E   ModuleNotFoundError: No module named 'shared_schemas.p002_sfe'
=========================== short test summary info ============================
ERROR tests/test_api.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 4.18s ===============================
```
**Status: FAILED :x:**

## SG_proj_003
```text
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-9.0.3, pluggy-1.5.0
rootdir: /Users/hyunchanan/Documents/GitHub/SG_proj_003
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.1.0, hypothesis-6.155.7, hydra-core-1.3.2, respx-0.23.1
collected 1 item

tests/test_import.py .                                                   [100%]

============================== 1 passed in 0.06s ===============================
```
**Status: PASSED :white_check_mark:**

## SG_proj_004
```text
============================= test session starts ==============================
platform linux -- Python 3.10.20, pytest-9.1.1, pluggy-1.6.0
rootdir: /app/SG_proj_004
configfile: pyproject.toml
plugins: asyncio-1.4.0, anyio-4.14.2
asyncio: mode=strict, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 5 items

tests/test_main.py .....                                                 [100%]

=============================== warnings summary ===============================
../../usr/local/lib/python3.10/site-packages/fastapi/testclient.py:1
  /usr/local/lib/python3.10/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================= 5 passed, 1 warning in 1.74s =========================
```
**Status: PASSED :white_check_mark:**

## SG_proj_005
```text
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-9.0.3, pluggy-1.5.0
rootdir: /Users/hyunchanan/Documents/GitHub/SG_proj_005
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.1.0, hypothesis-6.155.7, hydra-core-1.3.2, respx-0.23.1
collected 7 items

tests/test_inference.py .....                                            [ 71%]
tests/test_train.py ..                                                   [100%]

============================== 7 passed in 1.60s ===============================
```
**Status: PASSED :white_check_mark:**

## SG_proj_006
