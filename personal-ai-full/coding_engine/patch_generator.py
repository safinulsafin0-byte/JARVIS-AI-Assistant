# ============================================================
# JARVIS PATCH GENERATOR v5.1
# CODE MODIFICATION INTELLIGENCE ENGINE
#
# Impact + Dependency + Source Extraction
# ============================================================


from pathlib import Path
import json
import ast


from coding_engine.impact_analyzer import analyze





# ============================================================
# PATHS
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

        print(
            "[PATCH] function_index missing"
        )

        return {}



    try:

        raw = json.loads(

            FUNCTION_DB.read_text(

                encoding="utf-8"

            )

        )


        database = {}



        # ----------------------------
        # List format
        # ----------------------------

        if isinstance(raw, list):


            for item in raw:


                if not isinstance(
                    item,
                    dict
                ):

                    continue



                name = item.get(
                    "function"
                )


                if name:

                    database[name] = item



        # ----------------------------
        # Dictionary format
        # ----------------------------

        elif isinstance(raw, dict):


            for key,value in raw.items():


                if isinstance(
                    value,
                    dict
                ):


                    name = value.get(

                        "function",

                        key

                    )


                    database[name] = value



        return database



    except Exception as e:


        print(

            "[PATCH DB ERROR]",

            e

        )


        return {}







# ============================================================
# FIND REAL SOURCE FILE
# ============================================================


def locate_file(filename):


    filename = Path(filename)



    candidates = []



    # direct

    candidates.append(

        BASE_DIR / filename

    )



    # recursive search

    candidates.extend(

        BASE_DIR.rglob(

            filename.name

        )

    )



    for file in candidates:


        if file.exists():

            return file



    return None







# ============================================================
# EXTRACT FUNCTION SOURCE
# ============================================================


def extract_function_source(

        file_path,

        function_name

):


    source_file = locate_file(

        file_path

    )



    if not source_file:


        print(

            "[PATCH] File not found:",

            file_path

        )


        return ""





    try:


        code = source_file.read_text(

            encoding="utf-8",

            errors="ignore"

        )



        tree = ast.parse(

            code

        )



        for node in ast.walk(tree):


            if isinstance(

                node,

                ast.FunctionDef

            ):


                if node.name == function_name:


                    lines = code.splitlines()



                    return "\n".join(

                        lines[

                            node.lineno-1:

                            node.end_lineno

                        ]

                    )



    except Exception as e:


        print(

            "[SOURCE ERROR]",

            e

        )



    return ""









# ============================================================
# PATCH TYPE
# ============================================================


def detect_patch_type(request):


    request = request.lower()



    if "replace" in request:

        return "REPLACE"



    if "add" in request:

        return "EXTEND"



    if "fix" in request:

        return "BUGFIX"



    return "MODIFY"









# ============================================================
# CREATE PATCH PLAN
# ============================================================


def generate_patch_plan(

        function,

        request

):


    impact = analyze(

        function

    )



    if "error" in impact:


        return impact





    target = impact["target"]



    current_code = extract_function_source(

        target["file"],

        function

    )





    plan = {


        "request":

            request,



        "patch_type":

            detect_patch_type(

                request

            ),



        "target":

            target,



        "risk":

            impact["risk"],



        "current_code":

            current_code,



        "callers":

            impact["callers"],



        "dependencies":

            impact["dependencies"],



        "files":

            impact["files"],



        "strategy":[],



        "tests":[]

    }







    # ========================================================
    # STRATEGY
    # ========================================================


    plan["strategy"].append(

        "Create backup before modification"

    )



    plan["strategy"].append(

        f"Modify {function}() implementation"

    )



    for dep in impact["dependencies"]:


        plan["strategy"].append(

            f"Review dependency: {dep}()"

        )





    for caller in impact["callers"]:


        plan["strategy"].append(

            "Verify caller compatibility: "

            +

            caller["function"]

            +

            "()"

        )








    # ========================================================
    # TESTS
    # ========================================================


    plan["tests"] = [


        "Target function execution test",


        "API endpoint validation",


        "Dependency regression test",


        "Affected file validation"

    ]



    return plan







# ============================================================
# REPORT
# ============================================================


def print_patch_plan(

        function,

        request

):


    result = generate_patch_plan(

        function,

        request

    )



    print()

    print(

        "🔥 JARVIS PATCH GENERATOR v5.1"

    )

    print(

        "="*60

    )



    if "error" in result:


        print(

            result["error"]

        )


        return






    print(

        "\nREQUEST:"

    )


    print(

        result["request"]

    )





    target = result["target"]



    print(

        "\nTARGET:"

    )


    print(

        target["function"]

    )


    print(

        "FILE:",

        target["file"]

    )


    print(

        "LINE:",

        target["line"]

    )






    print(

        "\nPATCH TYPE:",

        result["patch_type"]

    )



    print(

        "\nRISK:",

        result["risk"]

    )








    print(

        "\nCURRENT IMPLEMENTATION:"

    )


    if result["current_code"]:


        print(

            result["current_code"]

        )


    else:


        print(

            "[SOURCE NOT FOUND]"

        )







    print(

        "\nPATCH STRATEGY:"

    )


    for i,item in enumerate(

        result["strategy"],

        1

    ):


        print(

            i,

            ".",

            item

        )






    print(

        "\nTEST PLAN:"

    )


    for test in result["tests"]:


        print(

            "✓",

            test

        )





    print(

        "\nAFFECTED FILES:"

    )


    for file in result["files"]:


        print(

            "-",

            file

        )







# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":



    print_patch_plan(

        "speak_async",

        "Replace speak_async with streaming TTS support"

    )