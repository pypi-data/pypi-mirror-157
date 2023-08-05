import subprocess
from typing import NamedTuple

_TIMEOUT_MESSAGE = 'Command "{}" timed out.'
_SHELL_TIMEOUT = 1000


class ProcessResult(NamedTuple):
    stdout: str
    exit_code: int
    error_message: str


class ProcessTimeoutError(Exception):
    def __init__(self, command: str):
        super().__init__(_TIMEOUT_MESSAGE.format(command))


class Process:  # pylint: disable=too-few-public-methods
    __slots__ = ('_shell_process', )

    _shell_process: subprocess.Popen

    def _run(self, command: str) -> ProcessResult:
        self._shell_process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True,
        )

        try:
            stdout, stderr = self._shell_process.communicate(timeout=_SHELL_TIMEOUT)
        except TimeoutError:
            self._shell_process.kill()
            raise ProcessTimeoutError(command)

        return ProcessResult(stdout=stdout, exit_code=self._shell_process.returncode, error_message=stderr)
