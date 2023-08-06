import os
import shutil
from contextlib import contextmanager
from pathlib import Path

from vst.classes.process import Process, ProcessResult  # type: ignore

_PROCESS_FAILED = 'Shell command failed with exit code: {} \nError message: \n{}.'


class ShellProcessFailedError(Exception):
    def __init__(self, exit_code: int, error_message: str):
        super().__init__(_PROCESS_FAILED.format(exit_code, error_message))


class Shell(Process):

    def run(self, command: str) -> ProcessResult:
        shell_results = self._run(f'bash -c -i {command}')

        if shell_results.exit_code:
            raise ShellProcessFailedError(shell_results.exit_code, shell_results.error_message)

        return shell_results

    @staticmethod
    @contextmanager
    def cd(path: str) -> None:
        start_path = os.getcwd()
        try:
            os.chdir(path)
            yield
        finally:
            os.chdir(start_path)

    @staticmethod
    def mkdir(path: str, parent: bool = False) -> None:
        if parent:
            os.makedirs(path)
        else:
            os.mkdir(path)

    @staticmethod
    def move(source_path: str, destination_path: str) -> None:
        shutil.move(source_path, destination_path)

    @staticmethod
    def copy(source_path: str, destination_path: str) -> None:
        shutil.copy(source_path, destination_path)

    @staticmethod
    def rmtree(path: str) -> None:
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass

    @staticmethod
    def open(path: str) -> str:
        with open(path) as file:
            return file.read()

    @staticmethod
    def save(path: str, content: str) -> None:
        with open(path, 'w') as file:
            file.write(content)

    @staticmethod
    def get_files_by_extensions(path: str, extensions: str, recursive: bool = False) -> list:
        pattern = '**/*' if recursive else '*'
        return sum([sorted(Path(path).glob(f'{pattern}.{extension}')) for extension in extensions], [])
