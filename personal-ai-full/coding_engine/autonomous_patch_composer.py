# ============================================================
# JARVIS AUTONOMOUS PATCH COMPOSER v7.0
#
# SAFE REFACTOR STRATEGY ENGINE
#
# Converts validator failures into safe patch requirements
# ============================================================


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

            item["function"]: item

            for item in data

            if "function" in item

        }


    return data





# ============================================================
# FIND FUNCTION
# ============================================================


def find_function(name):


    db = load_database()



    for key,value in db.items():


        if key.lower() == name.lower():

            return value



    return None





# ============================================================
# REQUIREMENT ANALYSIS
# ============================================================


def analyze_failures(warnings):


    preserve = []

    returns = []



    for warning in warnings:


        w = warning.lower()



        if "generate_wav" in w:

            preserve.append(
                "generate_wav"
            )


        if "stop" in w:

            preserve.append(
                "stop"
            )


        if "clean_text" in w:

            preserve.append(
                "clean_text"
            )


        if "duration_ms" in w:

            returns.append(
                "duration_ms"
            )


        if "started" in w:

            returns.append(
                "started"
            )


        if "error" in w:

            returns.append(
                "error"
            )


        if "offline" in w:

            returns.append(
                "offline"
            )


        if "text" in w:

            returns.append(
                "text"
            )



    return {

        "preserve_dependencies":
            list(set(preserve)),


        "preserve_returns":
            list(set(returns))

    }





# ============================================================
# COMPOSE PLAN
# ============================================================


def compose_patch(

        function,

        request,

        warnings

):


    info = find_function(function)



    if not info:


        return {

            "error":
            "Function not found"

        }



    requirements = analyze_failures(

        warnings

    )



    return {


        "target":{


            "function":
                function,


            "file":
                info.get("file"),


            "line":
                info.get("line")

        },


        "request":

            request,


        "patch_type":

            "SAFE_REFACTOR",


        "must_preserve":

            requirements["preserve_dependencies"],


        "return_contract":

            requirements["preserve_returns"],


        "status":

            "READY_FOR_CODE_GENERATION"

    }





# ============================================================
# REPORT
# ============================================================


def print_report(result):


    print()

    print(
        "🔥 JARVIS AUTONOMOUS PATCH COMPOSER v7.0"
    )

    print(
        "="*60
    )


    if "error" in result:

        print(result["error"])

        return



    print()

    print("TARGET:")

    print(
        result["target"]["function"]
    )


    print(
        "FILE:",
        result["target"]["file"]
    )


    print(
        "LINE:",
        result["target"]["line"]
    )



    print()

    print(
        "PATCH TYPE:"
    )


    print(
        result["patch_type"]
    )



    print()

    print(
        "PRESERVE:"
    )


    for x in result["must_preserve"]:

        print(
            "✓",
            x
        )



    print()

    print(
        "RETURN CONTRACT:"
    )


    for x in result["return_contract"]:

        print(
            "✓",
            x
        )



    print()

    print(
        "STATUS:"
    )


    print(
        result["status"]
    )





# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":


    warnings = [

        "Removed dependency: generate_wav()",

        "Removed dependency: stop()",

        "Removed dependency: clean_text()",

        "Return field removed: duration_ms",

        "Return field removed: error"

    ]



    result = compose_patch(

        "speak_async",

        "Replace speak_async with streaming TTS support",

        warnings

    )


    print_report(result)