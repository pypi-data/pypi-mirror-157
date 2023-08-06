def test_fixture(testdir):
    testdir.makepyfile(
        """
    import sys
    import pytest

    def test_fixture(run_subprocess):
        if sys.platform in ('linux', 'cygwin', 'darwin'):  # ie we are on a Linux-like OS
            command_line_arguments = ('ls', '-l')
        else:
            command_line_arguments = ('dir',)

        result = run_subprocess(*command_line_arguments)

        assert result.exit_code == 0
        assert result.stderr == ''
        assert 'test_fixture.py' in result.stdout
    """
    )
    result = testdir.runpytest("--verbose")
    result.stdout.fnmatch_lines("test_fixture.py::test_fixture PASSED*")
