# ============================================================
# JARVIS ADVANCED CODE REASONING ENGINE v8.2
#
# Multi-file reasoning
# Impact prediction
# Test suggestion
# Architecture awareness
#
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
# LOAD CODE KNOWLEDGE
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
# FUNCTION SEARCH
# ============================================================


def find_related_functions(keyword):


    database = load_database()


    results=[]


    keyword = keyword.lower()



    for name,data in database.items():


        score=0



        if keyword in name.lower():

            score+=10



        calls = data.get(
            "calls",
            []
        )



        for call in calls:


            if keyword in call.lower():

                score+=5




        if score:


            results.append(

                {

                    "function":name,

                    "file":data.get(
                        "file"
                    ),

                    "score":score,

                    "calls":calls

                }

            )



    results.sort(

        key=lambda x:x["score"],

        reverse=True

    )


    return results







# ============================================================
# IMPACT PREDICTION
# ============================================================


def predict_impact(function):


    database = load_database()


    affected=[]



    for name,data in database.items():


        calls=data.get(
            "calls",
            []
        )


        if function in calls:


            affected.append(

                {

                "function":name,

                "file":data.get(
                    "file"
                )

                }

            )



    return affected







# ============================================================
# RISK ANALYZER
# ============================================================


def calculate_risk(

        dependencies,

        callers

):


    score=0



    score += len(dependencies)*10

    score += len(callers)*15



    if score > 60:

        return "HIGH"


    elif score > 30:

        return "MEDIUM"


    return "LOW"








# ============================================================
# TEST GENERATOR
# ============================================================


def generate_tests(function):


    return [

        f"test_{function}_success",

        f"test_{function}_invalid_input",

        f"test_{function}_dependency_failure"

    ]









# ============================================================
# REASONING ENGINE
# ============================================================


def reason_about_change(

        function,

        request

):


    database=load_database()



    target = database.get(
        function,
        {}
    )



    dependencies = target.get(
        "calls",
        []
    )



    callers = predict_impact(
        function
    )



    risk = calculate_risk(

        dependencies,

        callers

    )



    result={


        "target":

        function,


        "request":

        request,


        "dependencies":

        dependencies,


        "affected_files":

        callers,


        "risk":

        risk,


        "suggested_tests":

        generate_tests(
            function
        )


    }



    return result







# ============================================================
# REPORT
# ============================================================


def print_report(data):


    print()

    print(
        "🔥 JARVIS CODE REASONING ENGINE v8.2"
    )

    print(
        "="*60
    )


    print()


    print(
        "TARGET:",
        data["target"]
    )


    print()


    print(
        "DEPENDENCIES:"
    )


    for x in data["dependencies"]:

        print(
            "↓",
            x
        )


    print()


    print(
        "AFFECTED:"
    )


    for x in data["affected_files"]:

        print(

            "↑",

            x["function"],

            "[",

            x["file"],

            "]"

        )


    print()


    print(
        "RISK:",
        data["risk"]
    )


    print()


    print(
        "GENERATED TESTS:"
    )


    for t in data["suggested_tests"]:

        print(
            "✓",
            t
        )









# ============================================================
# TEST
# ============================================================


if __name__=="__main__":



    result = reason_about_change(

        "speak_async",

        "Replace speak_async with streaming TTS support"

    )


    print_report(result)