# ============================================================
# JARVIS AUTONOMOUS DEBUGGER v7.9
#
# Error Analysis + Root Cause Detection Engine
#
# ============================================================


import re
import traceback

from voice.tts import generate_wav






# ============================================================
# ERROR ANALYZER
# ============================================================


def analyze_error(error):


    message = str(error)

    trace = traceback.format_exc()



    result = {


        "error":
            message,


        "type":
            None,


        "function":
            None,


        "suggestion":
            None

    }







    # ========================================================
    # ERROR TYPE DETECTION
    # ========================================================


    error_types = [

        "NameError",

        "TypeError",

        "AttributeError",

        "ImportError",

        "ModuleNotFoundError",

        "FileNotFoundError",

        "ValueError"

    ]



    for err in error_types:


        if err in trace or err in message:


            result["type"] = err

            break







    # ========================================================
    # NAME ERROR
    # ========================================================


    match = re.search(

        r"name '(.+?)' is not defined",

        message

    )


    if match:


        func = match.group(1)


        result["function"] = func


        result["suggestion"] = (

            f"Missing dependency: {func}. "

            "Search function index or create replacement."

        )


        return result







    # ========================================================
    # TYPE ERROR
    # ========================================================


    if result["type"] == "TypeError":


        match = re.search(

            r"(\w+)\(\) missing (\d+) required positional arguments?: (.+)",

            message

        )



        if match:


            func = match.group(1)

            count = match.group(2)

            args = match.group(3)



            result["function"] = func



            result["suggestion"] = (

                f"{func}() requires {count} "

                f"more argument(s): {args}. "

                "Check caller and function signature."

            )



            return result





        match = re.search(

            r"(\w+)\(\) takes .* but .* were given",

            message

        )


        if match:


            result["function"] = match.group(1)


            result["suggestion"] = (

                "Function signature mismatch. "

                "Compare caller arguments with definition."

            )


            return result







    # ========================================================
    # ATTRIBUTE ERROR
    # ========================================================


    match = re.search(

        r"has no attribute '(.+?)'",

        message

    )


    if match:


        attr = match.group(1)


        result["function"] = attr


        result["suggestion"] = (

            f"Missing attribute or method: {attr}. "

            "Check class implementation."

        )


        return result







    # ========================================================
    # IMPORT ERROR
    # ========================================================


    if "No module named" in message:


        match = re.search(

            r"No module named '(.+?)'",

            message

        )


        module = (

            match.group(1)

            if match

            else None

        )



        result["function"] = module



        result["suggestion"] = (

            "Install missing package or fix import path."

        )


        return result







    # ========================================================
    # FILE ERROR
    # ========================================================


    if "No such file" in message:


        result["suggestion"] = (

            "Check file path and file availability."

        )


        return result







    # Default

    result["suggestion"] = (

        "Analyze traceback and inspect affected dependency."

    )


    return result











# ============================================================
# DEBUG REPORT
# ============================================================


def debug_report(error):


    data = analyze_error(error)



    print()

    print(

        "🔥 JARVIS AUTONOMOUS DEBUGGER v7.9"

    )


    print(

        "="*60

    )


    print()


    print(

        "ERROR:"

    )

    print(

        data["error"]

    )



    print()


    print(

        "TYPE:",

        data["type"]

    )



    print(

        "FUNCTION:",

        data["function"]

    )



    print()


    print(

        "SUGGESTION:"

    )


    print(

        data["suggestion"]

    )









# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":



    print(

        "🔥 JARVIS AUTONOMOUS DEBUGGER v7.9"

    )



    print(

        "="*60

    )



    try:


        # intentional error test

        generate_wav()



    except Exception as e:


        debug_report(e)