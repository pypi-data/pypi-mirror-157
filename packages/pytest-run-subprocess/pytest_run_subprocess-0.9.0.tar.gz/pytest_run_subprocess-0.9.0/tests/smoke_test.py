def test_import_module():
    import pytest_run_subprocess

    assert pytest_run_subprocess is not None

    from pytest_run_subprocess.fixtures import run_subprocess

    assert run_subprocess is not None
