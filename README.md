[![Build Status](https://dev.azure.com/asottile/asottile/_apis/build/status/asottile.flake8-2020?branchName=master)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=27&branchName=master)
[![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/asottile/asottile/27/master.svg)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=27&branchName=master)

flake8-2020
===========

flake8 plugin which checks for misuse of `sys.version` or `sys.version_info`

this will become a problem when `python3.10` or `python4.0` exists (presumably
during the year 2020).

you might also find an early build of [python3.10] useful

[python3.10]: https://github.com/asottile/python3.10

## installation

`pip install flake8-2020`

## flake8 codes

| Code   | Description                                                         |
|--------|---------------------------------------------------------------------|
| YTT101 | `sys.version[:...]` referenced (python3.10), use `sys.version_info` |
| YTT102 | `sys.version[2]` referenced (python3.10), use `sys.version_info`    |
| YTT201 | `sys.version_info[0] == 3` referenced (python4), use `>=`           |
| YTT202 | `six.PY3` referenced (python4), use `not six.PY2`                   |
| YTT301 | `sys.version[0]` referenced (python10), use `sys.version_info`      |

## rationale

lots of code incorrectly references the `sys.version` and `sys.version_info`
members.  in particular, this will cause some issues when the version of python
after python3.9 is released.  my current recommendation is 3.10 since I believe
it breaks less code, here's a few patterns that will cause issues:

```python
# in python3.10 this will report as '3.1' (should be '3.10')
python_version = sys.version[:3]  # YTT101
# in python3.10 this will report as '1' (should be '10')
py_minor = sys.version[2]

# correct way to do this
python_version = '{}.{}'.format(*sys.version_info)
py_minor = str(sys.version_info[1])
```

```python
# in python4 this will report as `False` (and suddenly run python2 code!)
is_py3 = sys.version_info[0] == 3  # YTT201

# in python4 this will report as `False` (six violates YTT201!)
if six.PY3:  # YTT202
    print('python3!')

# correct way to do this
is_py3 = sys.version_info > (3,)
```

```python
# in python10 this will report as '1'
python_major_version = sys.version[0]  # YTT301

# correct way to do this
python_major_version = str(sys.version_info[0])
```

## as a pre-commit hook

See [pre-commit](https://github.com/pre-commit/pre-commit) for instructions

Sample `.pre-commit-config.yaml`:

```yaml
-   repo: https://gitlab.com/pycqa/flake8
    rev: 3.7.8
    hooks:
    -   id: flake8
        additional_dependencies: [flake8-2020==1.0.0]
```
