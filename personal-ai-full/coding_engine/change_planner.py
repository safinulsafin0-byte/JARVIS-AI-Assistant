# ============================================================
# JARVIS CHANGE PLANNER v4.1
# ENGINEERING MODIFICATION STRATEGY ENGINE
#
# Impact + Dependency Priority + Change Phases
# ============================================================


from pathlib import Path


from coding_engine.impact_analyzer import (
    analyze,
    find_function
)





# ============================================================
# CHANGE TYPE DETECTOR
# ============================================================


def detect_change_type(request):

    request = request.lower()



    if any(
        word in request
        for word in [
            "replace",
            "switch",
            "migrate",
            "convert"
        ]
    ):

        return "replacement"



    if any(
        word in request
        for word in [
            "add",
            "create",
            "implement",
            "support"
        ]
    ):

        return "feature"



    if any(
        word in request
        for word in [
            "fix",
            "bug",
            "error"
        ]
    ):

        return "bugfix"



    return "modification"





# ============================================================
# DEPENDENCY PRIORITY
# ============================================================


def dependency_priority(name):


    name = name.lower()



    critical = {

        "generate_wav",
        "stop",
        "speak_async"

    }



    support = {

        "clean_text",
        "_get_wav_duration_ms"

    }



    if name in critical:

        return (
            "★★★★★",
            5
        )



    if name in support:

        return (
            "★★★",
            3
        )



    return (
        "★★",
        2
    )





# ============================================================
# BUILD PLAN
# ============================================================


def generate_plan(
        function,
        request
):


    impact = analyze(
        function
    )



    if "error" in impact:

        return impact





    dependencies = sorted(

        impact["dependencies"],

        key=lambda x:

        dependency_priority(x)[1],

        reverse=True

    )



    plan = {


        "request":

            request,



        "change_type":

            detect_change_type(
                request
            ),



        "target":

            impact["target"],



        "risk":

            impact["risk"],



        "callers":

            impact["callers"],



        "core_dependencies":

            dependencies,



        "affected_files":

            impact["files"],



        "phases":[]

    }






    # ========================================================
    # PHASE 1
    # ========================================================


    plan["phases"].append(

        {

        "name":
            "ANALYSIS",


        "steps":[

            "Inspect target function signature",

            "Analyze dependency chain",

            "Check caller compatibility"

        ]

        }

    )





    # ========================================================
    # PHASE 2
    # ========================================================


    modify_steps=[


        f"Modify {function} implementation"


    ]



    for dep in dependencies:


        modify_steps.append(

            f"Review dependency: {dep}()"

        )



    plan["phases"].append(

        {

        "name":
            "IMPLEMENTATION",


        "steps":
            modify_steps

        }

    )





    # ========================================================
    # PHASE 3
    # ========================================================


    plan["phases"].append(

        {


        "name":
            "VALIDATION",



        "steps":[


            "Run function test",


            "Validate API contract",


            "Run regression checks"


        ]

        }

    )



    return plan





# ============================================================
# PRINT REPORT
# ============================================================


def print_plan(
        function,
        request
):


    result = generate_plan(

        function,

        request

    )



    print()


    print(

        "🔥 JARVIS CHANGE PLAN v4.1"

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





    target=result["target"]



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

        "\nRISK:",

        result["risk"]

    )





    print(

        "\nIMPACT:"

    )



    print(

        "\nCALLERS:"

    )



    for caller in result["callers"]:


        print(

            "↑",

            caller["function"],

            "[",

            caller["file"],

            "]"

        )





    print(

        "\nCORE DEPENDENCIES:"

    )



    for dep in result["core_dependencies"]:


        star,level = dependency_priority(

            dep

        )


        print(

            star,

            dep,

            "()"

        )





    print(

        "\nMODIFICATION PLAN:"

    )



    counter=1



    for phase in result["phases"]:


        print()


        print(

            phase["name"]

        )


        for step in phase["steps"]:


            print(

                counter,

                ".",

                step

            )


            counter += 1





    print(

        "\nAFFECTED FILES:"

    )



    for file in result["affected_files"]:


        print(

            "-",

            file

        )





# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    print_plan(

        "speak_async",

        "Replace speak_async with streaming TTS support"

    )