import ast

import pytest

from flake8_2020 import Plugin


def results(s):
    return {'{}:{}: {}'.format(*r) for r in Plugin(ast.parse(s)).run()}


@pytest.mark.parametrize(
    's',
    (
        '',
        'import sys\nprint(sys.version)',
        'import sys\nprint("{}.{}".format(*sys.version_info))',
        'PY3 = sys.version_info[0] >= 3',
        # ignore from imports with aliases, patches welcome
        'from sys import version as v\nprint(v[:3])',
    ),
)
def test_ok(s):
    assert results(s) == set()


@pytest.mark.parametrize(
    's',
    (
        'import sys\nprint(sys.version[:3])',
        'from sys import version\nprint(version[:3])',
    ),
)
def test_py310_slicing_of_sys_version_string(s):
    assert results(s) == {
        '2:6: YTT101: `sys.version[:...]` referenced (python3.10), use '
        '`sys.version_info`',
    }


@pytest.mark.parametrize(
    's',
    (
        'import sys\npy_minor = sys.version[2]',
        'from sys import version\npy_minor = version[2]',
    ),
)
def test_py310_indexing_of_sys_version_string(s):
    assert results(s) == {
        '2:11: YTT102: `sys.version[2]` referenced (python3.10), use '
        '`sys.version_info`',
    }


@pytest.mark.parametrize(
    's',
    (
        'from sys import version\nversion < "3.5"',
        'import sys\nsys.version < "3.5"',
        'import sys\nsys.version <= "3.5"',
        'import sys\nsys.version > "3.5"',
        'import sys\nsys.version >= "3.5"',
    ),
)
def test_py310_string_comparison(s):
    assert results(s) == {
        '2:0: YTT103: `sys.version` compared to string (python3.10), use '
        '`sys.version_info`',
    }


@pytest.mark.parametrize(
    's',
    (
        'import sys\nPY3 = sys.version_info[0] == 3',
        'from sys import version_info\nPY3 = version_info[0] == 3',
    ),
)
def test_py4_comparison_to_version_3(s):
    assert results(s) == {
        '2:6: YTT201: `sys.version_info[0] == 3` referenced (python4), use '
        '`>=`',
    }


@pytest.mark.parametrize(
    's',
    (
        'import six\n'
        'if six.PY3:\n'
        '    print("3")\n',

        'from six import PY3\n'
        'if PY3:\n'
        '    print("3")\n',
    ),
)
def test_py4_usage_of_six_py3(s):
    assert results(s) == {
        '2:3: YTT202: `six.PY3` referenced (python4), use `not six.PY2`',
    }


@pytest.mark.parametrize(
    's',
    (
        'import sys\npy_major = sys.version[0]',
        'from sys import version\npy_major = sys.version[0]',
    ),
)
def test_py10_indexing_of_sys_version_string(s):
    assert results(s) == {
        '2:11: YTT301: `sys.version[0]` referenced (python10), use '
        '`sys.version_info`',
    }


@pytest.mark.parametrize(
    's',
    (
        'import sys\nsys.version_info[1] >= 5',
        'from sys import version_info\nversion_info[1] < 6',
    ),
)
def test_version_info_index_one(s):
    assert results(s) == {
        '2:0: YTT203: `sys.version_info[1]` compared to integer, compare '
        '`sys.version_info` to tuple',
    }


@pytest.mark.parametrize(
    's',
    (
        'import sys\nsys.version_info.minor <= 7',
        'from sys import version_info\nversion_info.minor > 8',
    ),
)
def test_version_info_minor(s):
    assert results(s) == {
        '2:0: YTT204: `sys.version_info.minor` compared to integer, compare '
        '`sys.version_info` to tuple',
    }
