# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def run_subprocess():
    import subprocess
    import sys
    import typing as t

    class CLIResult:
        def __init__(self, completed_process: subprocess.CompletedProcess):
            self._exit_code = int(completed_process.returncode)
            self._stdout = str(completed_process.stdout, encoding='utf-8')
            self._stderr = str(completed_process.stderr, encoding='utf-8')

        @property
        def exit_code(self) -> int:
            return self._exit_code

        @property
        def stdout(self) -> str:
            return self._stdout

        @property
        def stderr(self) -> str:
            return self._stderr

    def python37_n_above_kwargs():
        return dict(
            capture_output=True,  # capture stdout and stderr separately
            # cwd=project_directory,
            check=True,
        )

    def python36_n_below_kwargs():
        return dict(
            stdout=subprocess.PIPE,  # capture stdout and stderr separately
            stderr=subprocess.PIPE,
            check=True,
        )

    subprocess_run_map = {
        True: python36_n_below_kwargs,
        False: python37_n_above_kwargs,
    }

    def get_callable(cli_args: t.List[str], **kwargs) -> t.Callable[[], CLIResult]:
        def subprocess_run() -> CLIResult:
            kwargs_dict = subprocess_run_map[sys.version_info < (3, 7)]()
            completed_process = subprocess.run(  # pylint: disable=W1510
                cli_args, **dict(dict(kwargs_dict, **kwargs), check=True)
            )
            return CLIResult(completed_process)

        return subprocess_run

    def execute_command_in_subprocess(executable: str, *args, **kwargs):
        execute_subprocess = get_callable([executable] + list(args), **kwargs)
        return execute_subprocess()

    return execute_command_in_subprocess
