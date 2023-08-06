"""pytest file built from C:/Users/Turtor/ownCloud/Github/mypythontools/README.md"""
import pytest

from phmdoctest.functions import _phm_compare_exact


def test_code_71():
    from mypythontools import helpers

    # Caution- no assertions.


@pytest.mark.skip()
def test_code_78_output_196(capsys):
    import mypythontools

    helpers = mypythontools.helpers

    _phm_expected_str = """\
pip install -r requirements.txt
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
