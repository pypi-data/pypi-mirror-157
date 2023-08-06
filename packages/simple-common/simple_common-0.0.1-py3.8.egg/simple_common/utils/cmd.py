import subprocess
from subprocess import Popen


def exec_shell(command, callback=None):
    with Popen(command, stdin=None, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
               shell=True, encoding='utf8') as proc:
        proc.wait()
        return_code = proc.returncode
        stdout = proc.stdout.readlines()
        stderr = proc.stderr.readlines()

        result = dict(return_code=return_code,
                      stdout=stdout,
                      stderr=stderr)

        if callback:
            callback(result)

        return result


class ExecCommand:
    def __init__(self, cmd: str):
        self.cmd = cmd

    def prepare(self, **kwargs):
        self.cmd = self.cmd.format(**kwargs)
        return self

    def run(self):
        return exec_shell(self.cmd)
