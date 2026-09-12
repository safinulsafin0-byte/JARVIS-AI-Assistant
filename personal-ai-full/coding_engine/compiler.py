import subprocess
import uuid
from pathlib import Path


class CppCompiler:

    def __init__(self):
        self.compiler = "g++"

    def check_compiler(self):
        try:
            result = subprocess.run(
                [self.compiler, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "available": result.returncode == 0,
                "output": result.stdout.strip()
            }

        except FileNotFoundError:
            return {
                "available": False,
                "output": "g++ was not found in PATH."
            }

        except Exception as error:
            return {
                "available": False,
                "output": str(error)
            }

    def compile(self, code):

        workspace = (
            Path(__file__).resolve().parent
            / "workspace"
        )

        workspace.mkdir(
            parents=True,
            exist_ok=True
        )

        uid = uuid.uuid4().hex

        source = (
            workspace /
            f"solution_{uid}.cpp"
        )

        executable = (
            workspace /
            f"solution_{uid}.exe"
        )

        try:

            source.write_text(
                code,
                encoding="utf-8"
            )

            command = [
                self.compiler,
                "-std=c++17",
                "-O2",
                "-Wall",
                "-Wextra",
                str(source),
                "-o",
                str(executable)
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "source": str(source),
                "executable": (
                    str(executable)
                    if executable.exists()
                    else None
                )
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "stdout": "",
                "stderr": "COMPILATION TIMEOUT",
                "source": str(source),
                "executable": None
            }

        except Exception as error:

            return {
                "success": False,
                "stdout": "",
                "stderr": str(error),
                "source": str(source),
                "executable": None
            }

    def run(
        self,
        executable,
        input_data="",
        timeout=3
    ):

        try:

            result = subprocess.run(
                [executable],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "TIME LIMIT EXCEEDED"
            }

        except Exception as error:

            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(error)
            }

    def cleanup(
        self,
        source=None,
        executable=None
    ):

        for file_path in [source, executable]:

            if not file_path:
                continue

            try:
                Path(file_path).unlink(
                    missing_ok=True
                )
            except Exception:
                pass