# ============================================================
# JARVIS PATCH SIMULATOR v7.6
#
# Virtual Patch Testing Engine
#
# Before real modification:
# - AST validation
# - Dependency validation
# - Risk analysis
#
# ============================================================


import ast
import json
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent


FUNCTION_DB = (
    BASE_DIR
    /
    "memory"
    /
    "function_index.json"
)





# ============================================================
# LOAD DATABASE
# ============================================================


def load_database():

    if not FUNCTION_DB.exists():

        return {}


    data = json.loads(

        FUNCTION_DB.read_text(
            encoding="utf-8"
        )

    )


    if isinstance(data,list):

        return {

            x["function"]:x

            for x in data

            if "function" in x

        }


    return data







# ============================================================
# CHECK SYNTAX
# ============================================================


def check_ast(code):

    try:

        ast.parse(code)

        return True,None


    except Exception as e:

        return False,str(e)









# ============================================================
# EXTRACT CALLS
# ============================================================


def extract_calls(code):

    calls=[]


    tree=ast.parse(code)


    for node in ast.walk(tree):


        if isinstance(node,ast.Call):


            if isinstance(
                node.func,
                ast.Name
            ):

                calls.append(
                    node.func.id
                )


            elif isinstance(
                node.func,
                ast.Attribute
            ):

                calls.append(
                    node.func.attr
                )


    return list(set(calls))







# ============================================================
# DEPENDENCY CHECK
# ============================================================


def dependency_check(code):


    database = load_database()


    available=set(
        database.keys()
    )


    builtin={

        "print",
        "str",
        "int",
        "float",
        "len",
        "list",
        "dict",
        "set",
        "Exception"

    }


    missing=[]


    for call in extract_calls(code):


        if (

            call not in available

            and

            call not in builtin

        ):

            missing.append(call)



    return missing







# ============================================================
# SIMULATION ENGINE
# ============================================================


def simulate_patch(

        file,

        function,

        new_code

):


    result={

        "file":file,

        "function":function,

        "checks":[],

        "risk":"LOW"

    }



    # AST

    valid,error = check_ast(
        new_code
    )


    if valid:

        result["checks"].append(
            "✓ AST syntax valid"
        )

    else:

        result["checks"].append(
            "❌ AST error: "+error
        )

        result["risk"]="BLOCKED"

        return result






    # Dependencies

    missing = dependency_check(
        new_code
    )


    if missing:


        result["checks"].append(

            "❌ Missing dependencies: "

            +

            str(missing)

        )

        result["risk"]="HIGH"


    else:


        result["checks"].append(
            "✓ Dependencies available"
        )





    # Function preservation

    if function in new_code:


        result["checks"].append(

            "✓ Function preserved"

        )


    else:


        result["checks"].append(

            "❌ Function missing"

        )

        result["risk"]="BLOCKED"




    return result







# ============================================================
# REPORT
# ============================================================


def print_report(result):


    print()

    print(
        "🔥 JARVIS PATCH SIMULATOR v7.6"
    )

    print(
        "="*60
    )


    print()

    print(
        "TARGET:"
    )

    print(
        result["function"]
    )


    print(
        "FILE:",
        result["file"]
    )


    print()


    print(
        "VALIDATION:"
    )


    for c in result["checks"]:

        print(c)



    print()


    print(
        "RISK:",
        result["risk"]
    )



    if result["risk"]!="BLOCKED":

        print()

        print(
            "STATUS: READY FOR EXECUTION"
        )

    else:

        print()

        print(
            "STATUS: PATCH BLOCKED"
        )







# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    new_function="""


def speak_async(text):

    cleaned=clean_text(text)

    stop()

    generate_wav(
        cleaned,
        "test.wav"
    )

    return {

        "success":True

    }

"""


    result=simulate_patch(

        "tts.py",

        "speak_async",

        new_function

    )


    print_report(result)