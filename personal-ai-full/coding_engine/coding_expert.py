# ============================================================
# JARVIS CODING EXPERT
# Generate -> Compile -> Test -> Repair
# ============================================================

import re

from .compiler import CppCompiler


class CodingExpert:

    def __init__(self, llm_function):
        self.llm_function = llm_function
        self.compiler = CppCompiler()
        self.max_repair_attempts = 3

    # ========================================================
    # EXTRACT CODE
    # ========================================================

    def extract_code(self, response):

        if not response:
            return ""

        response = str(response).strip()

        # ----------------------------------------------------
        # Markdown code block
        # ----------------------------------------------------

        match = re.search(
            r"```(?:cpp|c\+\+|cc|c)?\s*(.*?)```",
            response,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            return match.group(1).strip()

        # ----------------------------------------------------
        # Raw code
        # ----------------------------------------------------

        return response

    # ========================================================
    # BUILD SOLUTION PROMPT
    # ========================================================

    def build_solution_prompt(self, problem):

        return f"""
You are JARVIS Competitive Programming Expert.

Solve the following programming problem.

RULES:

1. Understand the complete problem.
2. Extract all constraints.
3. Identify the optimal algorithm.
4. Consider worst-case time complexity.
5. Consider memory complexity.
6. Check all edge cases.
7. Check integer overflow.
8. Use GNU C++17.
9. Read from stdin.
10. Write to stdout.
11. Do not use external libraries.
12. Do not hardcode sample answers.
13. The solution must work for all valid inputs.
14. Return ONLY C++17 source code.
15. Put the code inside a cpp code block.
16. Do not provide explanation outside the code.

==================================================
PROBLEM
==================================================

{problem}

==================================================
FINAL CODE
==================================================
"""

    # ========================================================
    # BUILD REPAIR PROMPT
    # ========================================================

    def build_repair_prompt(self, problem, code, error):

        return f"""
You are JARVIS Competitive Programming Debugger.

The following C++17 solution failed verification.

Find the bug and return a corrected solution.

RULES:

1. Re-read the original problem.
2. Check constraints.
3. Find the exact bug.
4. Fix the algorithm if necessary.
5. Preserve optimal complexity.
6. Check integer overflow.
7. Check boundary conditions.
8. Check input/output handling.
9. Do not hardcode samples.
10. Use GNU C++17.
11. Return ONLY corrected C++17 code.
12. Put the code inside a cpp code block.
13. Do not provide explanation.

==================================================
ORIGINAL PROBLEM
==================================================

{problem}

==================================================
CURRENT CODE
==================================================

```cpp
{code}
```

==================================================
ERROR / TEST RESULT
==================================================

{error}

==================================================
CORRECTED CODE
==================================================
"""

    # ========================================================
    # EXTRACT SAMPLES
    # ========================================================

    def extract_samples(self, problem):

        tests = []

        if not problem:
            return tests

        # ----------------------------------------------------
        # Input code blocks
        # ----------------------------------------------------

        input_matches = re.findall(
            r"(?:Input|input)\s*:?\s*"
            r"```(?:text|txt)?\s*(.*?)```",
            problem,
            re.IGNORECASE | re.DOTALL
        )

        # ----------------------------------------------------
        # Output code blocks
        # ----------------------------------------------------

        output_matches = re.findall(
            r"(?:Output|output)\s*:?\s*"
            r"```(?:text|txt)?\s*(.*?)```",
            problem,
            re.IGNORECASE | re.DOTALL
        )

        count = min(len(input_matches), len(output_matches))

        for i in range(count):
            tests.append({
                "input": input_matches[i].strip(),
                "output": output_matches[i].strip()
            })

        # ----------------------------------------------------
        # Support simple examples without code blocks
        #
        # Example:
        #
        # Input:
        # 5 7
        #
        # Output:
        # 12
        # ----------------------------------------------------

        if not tests:

            simple_pattern = re.compile(
                r"(?:Input|input)\s*:?\s*"
                r"(.*?)"
                r"(?:Output|output)\s*:?\s*"
                r"(.*?)(?="
                r"(?:Input|input)\s*:?"
                r"|$)",
                re.IGNORECASE | re.DOTALL
            )

            simple_matches = simple_pattern.findall(problem)

            for input_text, output_text in simple_matches:

                input_text = input_text.strip()
                output_text = output_text.strip()

                if input_text and output_text:

                    # Remove accidental markdown fences
                    input_text = re.sub(
                        r"^```(?:text|txt)?\s*",
                        "",
                        input_text,
                        flags=re.IGNORECASE
                    )

                    input_text = re.sub(r"\s*```$", "", input_text)

                    output_text = re.sub(
                        r"^```(?:text|txt)?\s*",
                        "",
                        output_text,
                        flags=re.IGNORECASE
                    )

                    output_text = re.sub(r"\s*```$", "", output_text)

                    tests.append({
                        "input": input_text.strip(),
                        "output": output_text.strip()
                    })

        # ----------------------------------------------------
        # Extra fallback:
        #
        # Handles:
        #
        # Input:
        # 5 7
        #
        # Output:
        # 12
        # ----------------------------------------------------

        if not tests:

            lines = problem.splitlines()

            input_index = None

            for i, line in enumerate(lines):
                if re.match(r"^\s*Input\s*:?\s*$", line, re.IGNORECASE):
                    input_index = i
                    break

            if input_index is not None:

                output_index = None

                for i in range(input_index + 1, len(lines)):
                    if re.match(r"^\s*Output\s*:?\s*$", lines[i], re.IGNORECASE):
                        output_index = i
                        break

                if output_index is not None:

                    input_lines = lines[input_index + 1:output_index]
                    output_lines = lines[output_index + 1:]

                    input_text = "\n".join(input_lines).strip()
                    output_text = "\n".join(output_lines).strip()

                    # Stop output at another section if needed
                    output_text = re.split(
                        r"\n\s*(?:Input|Explanation|Note|Notes)\s*:?",
                        output_text,
                        maxsplit=1,
                        flags=re.IGNORECASE
                    )[0].strip()

                    if input_text and output_text:
                        tests.append({
                            "input": input_text,
                            "output": output_text
                        })

        return tests

    # ========================================================
    # COMPILE CODE
    # ========================================================

    def compile_code(self, code):
        return self.compiler.compile(code)

    # ========================================================
    # RUN TESTS
    # ========================================================

    def run_tests(self, executable, tests):

        results = []

        for number, test in enumerate(tests, start=1):

            result = self.compiler.run(
                executable,
                input_data=test["input"],
                timeout=3
            )

            actual = result.get("stdout", "").strip()
            expected = test.get("output", "").strip()

            passed = (
                result.get("success", False)
                and actual == expected
            )

            results.append({
                "test": number,
                "passed": passed,
                "input": test["input"],
                "expected": expected,
                "actual": actual,
                "stderr": result.get("stderr", "")
            })

            # Stop at first failure
            if not passed:
                break

        return results

    # ========================================================
    # SOLVE
    # ========================================================

    def solve(self, problem):

        # ----------------------------------------------------
        # Validate problem
        # ----------------------------------------------------

        if not problem or not problem.strip():
            return {
                "success": False,
                "stage": "input",
                "verified": False,
                "error": "Problem statement is empty."
            }

        # ----------------------------------------------------
        # Extract sample tests
        # ----------------------------------------------------

        tests = self.extract_samples(problem)

        print(f"[CODING EXPERT] Samples detected: {len(tests)}")

        # ----------------------------------------------------
        # Initial generation
        # ----------------------------------------------------

        prompt = self.build_solution_prompt(problem)

        try:
            response = self.llm_function(prompt)
        except Exception as error:
            return {
                "success": False,
                "stage": "generation",
                "verified": False,
                "attempts": 1,
                "error": str(error)
            }

        code = self.extract_code(response)

        # ----------------------------------------------------
        # Validate generated code
        # ----------------------------------------------------

        if not code:
            return {
                "success": False,
                "stage": "generation",
                "verified": False,
                "attempts": 1,
                "error": "JARVIS did not generate C++ code."
            }

        # ----------------------------------------------------
        # Generate -> Compile -> Test -> Repair
        # ----------------------------------------------------

        for attempt in range(self.max_repair_attempts + 1):

            print(f"[CODING EXPERT] Verification attempt {attempt + 1}")

            # =================================================
            # COMPILE
            # =================================================

            compilation = self.compile_code(code)

            # -------------------------------------------------
            # Compilation failed
            # -------------------------------------------------

            if not compilation.get("success", False):

                compile_error = compilation.get(
                    "stderr", "Unknown compilation error."
                )

                print("[CODING EXPERT] Compilation failed.")

                # ---------------------------------------------
                # No attempts left
                # ---------------------------------------------

                if attempt >= self.max_repair_attempts:

                    self.compiler.cleanup(
                        compilation.get("source"),
                        compilation.get("executable")
                    )

                    return {
                        "success": False,
                        "stage": "compile",
                        "verified": False,
                        "attempts": attempt + 1,
                        "code": code,
                        "error": compile_error
                    }

                # ---------------------------------------------
                # Repair compilation error
                # ---------------------------------------------

                repair_prompt = self.build_repair_prompt(
                    problem, code, compile_error
                )

                try:
                    repaired = self.llm_function(repair_prompt)
                except Exception as error:
                    return {
                        "success": False,
                        "stage": "repair",
                        "verified": False,
                        "attempts": attempt + 1,
                        "code": code,
                        "error": str(error)
                    }

                code = self.extract_code(repaired)

                if not code:
                    return {
                        "success": False,
                        "stage": "repair",
                        "verified": False,
                        "attempts": attempt + 1,
                        "error": "Empty code returned during repair."
                    }

                continue

            # =================================================
            # NO SAMPLE TESTS
            # =================================================

            if not tests:

                self.compiler.cleanup(
                    compilation.get("source"),
                    compilation.get("executable")
                )

                return {
                    "success": True,
                    "stage": "compiled",
                    "verified": False,
                    "attempts": attempt + 1,
                    "reason": (
                        "No sample tests detected. "
                        "Code compiled successfully."
                    ),
                    "code": code
                }

            # =================================================
            # SAMPLE TESTS
            # =================================================

            test_results = self.run_tests(
                compilation["executable"],
                tests
            )

            all_passed = (
                len(test_results) == len(tests)
                and all(test["passed"] for test in test_results)
            )

            # -------------------------------------------------
            # All tests passed
            # -------------------------------------------------

            if all_passed:

                print("[CODING EXPERT] All sample tests passed.")

                self.compiler.cleanup(
                    compilation.get("source"),
                    compilation.get("executable")
                )

                return {
                    "success": True,
                    "stage": "verified",
                    "verified": True,
                    "attempts": attempt + 1,
                    "tests": test_results,
                    "code": code
                }

            # =================================================
            # FAILED TEST
            # =================================================

            failed_test = next(
                (test for test in test_results if not test["passed"]),
                None
            )

            if failed_test:
                error_text = (
                    "Sample test failed.\n\n"
                    "INPUT:\n" + failed_test["input"] + "\n\n"
                    "EXPECTED OUTPUT:\n" + failed_test["expected"] + "\n\n"
                    "ACTUAL OUTPUT:\n" + failed_test["actual"] + "\n\n"
                    "STDERR:\n" + failed_test["stderr"]
                )
            else:
                error_text = "Unknown sample test failure."

            print("[CODING EXPERT] Sample test failed.")

            # -------------------------------------------------
            # Cleanup before repair
            # -------------------------------------------------

            self.compiler.cleanup(
                compilation.get("source"),
                compilation.get("executable")
            )

            # -------------------------------------------------
            # No repair attempts left
            # -------------------------------------------------

            if attempt >= self.max_repair_attempts:
                return {
                    "success": False,
                    "stage": "testing",
                    "verified": False,
                    "attempts": attempt + 1,
                    "tests": test_results,
                    "code": code,
                    "error": error_text
                }

            # =================================================
            # REPAIR
            # =================================================

            repair_prompt = self.build_repair_prompt(
                problem, code, error_text
            )

            try:
                repaired = self.llm_function(repair_prompt)
            except Exception as error:
                return {
                    "success": False,
                    "stage": "repair",
                    "verified": False,
                    "attempts": attempt + 1,
                    "tests": test_results,
                    "code": code,
                    "error": str(error)
                }

            code = self.extract_code(repaired)

            if not code:
                return {
                    "success": False,
                    "stage": "repair",
                    "verified": False,
                    "attempts": attempt + 1,
                    "error": "JARVIS returned empty code during repair."
                }

        # ----------------------------------------------------
        # Safety fallback
        # ----------------------------------------------------

        return {
            "success": False,
            "stage": "unknown",
            "verified": False,
            "code": code
        }