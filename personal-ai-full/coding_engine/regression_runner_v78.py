# ============================================================
# JARVIS REGRESSION TEST RUNNER v7.8
#
# Post Patch Validation System
#
# ============================================================


import ast
import importlib.util
from pathlib import Path




# ============================================================
# AST CHECK
# ============================================================


def check_syntax(file):

    try:

        code = Path(file).read_text(
            encoding="utf-8"
        )

        ast.parse(code)

        return True, None


    except Exception as e:

        return False, str(e)






# ============================================================
# FUNCTION CHECK
# ============================================================


def function_exists(file, function):


    try:

        tree = ast.parse(

            Path(file).read_text(
                encoding="utf-8"
            )

        )


        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):

                if node.name == function:

                    return True



    except:

        pass


    return False







# ============================================================
# IMPORT CHECK
# ============================================================


def import_check(file):


    try:

        spec = importlib.util.spec_from_file_location(
            "test_module",
            file
        )


        module = importlib.util.module_from_spec(
            spec
        )


        spec.loader.exec_module(
            module
        )


        return True,None


    except Exception as e:

        return False,str(e)









# ============================================================
# REGRESSION ENGINE
# ============================================================


def run_regression(

        file,

        function

):


    result = {

        "file":file,

        "function":function,

        "tests":[],

        "status":"PASS"

    }





    ok,error = check_syntax(file)


    if ok:

        result["tests"].append(
            "✓ Syntax validation"
        )

    else:

        result["tests"].append(
            "❌ Syntax error: "+error
        )

        result["status"]="FAIL"






    if function_exists(
        file,
        function
    ):


        result["tests"].append(
            "✓ Function preserved"
        )


    else:


        result["tests"].append(
            "❌ Function missing"
        )

        result["status"]="FAIL"






    ok,error = import_check(file)


    if ok:

        result["tests"].append(
            "✓ Import validation"
        )


    else:

        result["tests"].append(
            "❌ Import failed: "+error
        )

        result["status"]="FAIL"





    return result







# ============================================================
# REPORT
# ============================================================


def print_report(result):


    print()

    print(
        "🔥 JARVIS REGRESSION TEST RUNNER v7.8"
    )

    print("="*60)


    print()

    print(
        "TARGET:"
    )

    print(
        result["function"]
    )



    print()

    print(
        "TESTS:"
    )


    for t in result["tests"]:

        print(t)



    print()

    print(
        "RESULT:",
        result["status"]
    )






# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    print(
        "🔥 JARVIS REGRESSION TEST RUNNER v7.8 READY"
    )