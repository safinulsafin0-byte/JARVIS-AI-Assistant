from .compiler import CppCompiler


class CodeRunner:
    def __init__(self):
        self.compiler = CppCompiler()

    def verify(self, code: str, tests=None):
        if tests is None:
            tests = []

        compile_result = self.compiler.compile(code)

        if not compile_result["success"]:
            return {
                "verified": False,
                "stage": "compile",
                "compile": compile_result,
                "tests": []
            }

        executable = compile_result["executable"]

        test_results = []

        try:
            for index, test in enumerate(tests, start=1):
                input_data = test.get("input", "")
                expected = test.get("output", "").strip()

                result = self.compiler.run(
                    executable,
                    input_data=input_data,
                    timeout=3
                )

                actual = result["stdout"].strip()

                passed = (
                    result["success"]
                    and actual == expected
                )

                test_results.append({
                    "test": index,
                    "passed": passed,
                    "input": input_data,
                    "expected": expected,
                    "actual": actual,
                    "stderr": result["stderr"]
                })

                if not passed:
                    return {
                        "verified": False,
                        "stage": "test",
                        "compile": compile_result,
                        "tests": test_results
                    }

            return {
                "verified": True,
                "stage": "complete",
                "compile": compile_result,
                "tests": test_results
            }

        finally:
            self.compiler.cleanup(
                compile_result.get("source_file"),
                compile_result.get("executable")
            )