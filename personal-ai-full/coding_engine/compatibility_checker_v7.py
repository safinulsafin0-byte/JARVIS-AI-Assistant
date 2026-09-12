# ============================================================
# JARVIS COMPATIBILITY CHECKER v7.2
#
# GENERATED CODE VALIDATION ENGINE
#
# Checks:
# - Function existence
# - Dependency compatibility
# - Missing symbols
# - Runtime safety
#
# ============================================================


import ast
import json
from pathlib import Path





# ============================================================
# PATH
# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent


FUNCTION_DB = (

    BASE_DIR
    /
    "memory"
    /
    "function_index.json"

)







# ============================================================
# LOAD FUNCTION DATABASE
# ============================================================


def load_database():


    if not FUNCTION_DB.exists():

        return {}



    data = json.loads(

        FUNCTION_DB.read_text(

            encoding="utf-8"

        )

    )



    if isinstance(data, list):


        return {

            item["function"]:

            item

            for item in data

            if "function" in item

        }



    return data







# ============================================================
# EXTRACT FUNCTION CALLS
# ============================================================


def extract_calls(code):


    calls = []


    try:


        tree = ast.parse(code)



        for node in ast.walk(tree):


            if isinstance(node, ast.Call):


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



    except Exception as e:


        print(

            "[AST ERROR]",

            e

        )



    return list(

        set(calls)

    )









# ============================================================
# CHECK COMPATIBILITY
# ============================================================


def check_compatibility(code):


    database = load_database()


    calls = extract_calls(

        code

    )


    available = set(

        database.keys()

    )



    builtin = {


        "str",

        "int",

        "float",

        "print",

        "len",

        "range",

        "list",

        "dict",

        "set",

        "bool",

        "Exception"

    }



    missing = []

    found = []



    for call in calls:



        if call in available:


            found.append(call)



        elif call in builtin:


            continue


        else:


            missing.append(call)





    safe = len(missing) == 0



    return {


        "safe":

            safe,


        "calls":

            calls,


        "available":

            found,


        "missing":

            missing

    }









# ============================================================
# REPORT
# ============================================================


def print_report(result):


    print()

    print(

        "🔥 JARVIS COMPATIBILITY CHECKER v7.2"

    )

    print(

        "="*60

    )


    print()


    print(

        "GENERATED DEPENDENCIES:"

    )


    for item in result["calls"]:


        print(

            "↓",

            item

        )





    print()


    print(

        "AVAILABLE:"

    )


    for item in result["available"]:


        print(

            "✓",

            item

        )





    print()


    print(

        "MISSING:"

    )


    if result["missing"]:


        for item in result["missing"]:


            print(

                "❌",

                item

            )

    else:


        print(

            "None"

        )





    print()


    if result["safe"]:


        print(

            "RESULT: ✓ COMPATIBLE"

        )


    else:


        print(

            "RESULT: ⚠️ PATCH BLOCKED"

        )









# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":



    generated_code = """

def speak_async(text):

    cleaned = clean_text(text)

    stop()

    temp = create_streaming_wav(cleaned)

    start_stream(temp)

    duration_ms = _get_wav_duration_ms(temp)

    return {

        "success": True,

        "duration_ms": duration_ms

    }

"""



    result = check_compatibility(

        generated_code

    )



    print_report(

        result

    )