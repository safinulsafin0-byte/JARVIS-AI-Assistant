# ============================================================
# JARVIS IMPACT ANALYZER v3.2
# SMART DEPENDENCY FILTER ENGINE
#
# CHANGE IMPACT + CORE DEPENDENCY ANALYSIS
# ============================================================


from pathlib import Path
import json



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
# FUNCTION FILTER RULES
# ============================================================


IGNORE_FUNCTIONS = {

    "log",
    "print",
    "debug",
    "logger",
    "model_exists",
    "exists",
    "get",
    "set",
    "append",
    "close"

}



LOW_PRIORITY_FUNCTIONS = {

    "_get_wav_duration_ms",
    "clean_text"

}



HIGH_PRIORITY_FUNCTIONS = {

    "generate_wav",
    "stop",
    "speak_async"

}





# ============================================================
# LOAD DATABASE
# ============================================================


def load_database():


    if not FUNCTION_DB.exists():

        print(
            "[ERROR] function_index.json missing"
        )

        return {}



    raw = json.loads(

        FUNCTION_DB.read_text(
            encoding="utf-8"
        )

    )


    database = {}



    # dictionary format

    if isinstance(raw, dict):


        for key,value in raw.items():


            if isinstance(value, dict):


                name = value.get(
                    "function",
                    key
                )


                database[name] = value



    # list format

    elif isinstance(raw,list):


        for item in raw:


            if not isinstance(
                item,
                dict
            ):

                continue



            name=item.get(
                "function"
            )


            if name:

                database[name]=item



    return database





# ============================================================
# FIND FUNCTION
# ============================================================


def find_function(name):


    database = load_database()



    for func,data in database.items():


        if func.lower() == name.lower():

            return data



    return None





# ============================================================
# PROJECT FUNCTION CHECK
# ============================================================


def is_project_function(
        name,
        database
):


    return name in database





# ============================================================
# CORE DEPENDENCY ENGINE
# ============================================================


def project_dependencies(function):


    database = load_database()



    data = find_function(
        function
    )



    if not data:

        return []



    dependencies=[]



    for call in data.get(
        "calls",
        []
    ):



        # only project functions

        if not is_project_function(
            call,
            database
        ):

            continue



        # remove noise

        if call.lower() in IGNORE_FUNCTIONS:

            continue



        dependencies.append(
            call
        )



    return list(
        dict.fromkeys(
            dependencies
        )
    )





# ============================================================
# CALLERS
# ============================================================


def find_callers(function):


    database = load_database()


    callers=[]



    for name,data in database.items():


        for call in data.get(
            "calls",
            []
        ):


            if call.lower()==function.lower():


                callers.append(
                    data
                )



    return callers





# ============================================================
# AFFECTED FILES
# ============================================================


def affected_files(function):


    files=set()



    target=find_function(
        function
    )



    if target:


        files.add(
            target.get(
                "file",
                ""
            )
        )



    for caller in find_callers(
        function
    ):


        files.add(
            caller.get(
                "file",
                ""
            )
        )



    return [

        x

        for x in files

        if x

    ]





# ============================================================
# PRIORITY
# ============================================================


def dependency_priority(name):


    name=name.lower()



    if name in HIGH_PRIORITY_FUNCTIONS:

        return 3



    if name in LOW_PRIORITY_FUNCTIONS:

        return 1



    return 2





# ============================================================
# RISK ENGINE
# ============================================================


def calculate_risk(function):


    callers=len(
        find_callers(
            function
        )
    )


    deps=len(
        project_dependencies(
            function
        )
    )



    score=(

        callers*5

        +

        deps*3

    )



    if score>=15:

        return "HIGH"



    elif score>=5:

        return "MEDIUM"



    return "LOW"





# ============================================================
# COMPLETE ANALYSIS
# ============================================================


def analyze(function):


    data=find_function(
        function
    )



    if not data:


        return {

            "error":
            "Function not found"

        }



    return {


        "target":{


            "function":
            function,


            "file":
            data.get(
                "file"
            ),


            "line":
            data.get(
                "line"
            )

        },



        "callers":[


            {


            "function":
            x.get(
                "function"
            ),


            "file":
            x.get(
                "file"
            )


            }

            for x in find_callers(
                function
            )

        ],



        "dependencies":

            project_dependencies(
                function
            ),



        "files":

            affected_files(
                function
            ),



        "risk":

            calculate_risk(
                function
            )

    }





# ============================================================
# REPORT
# ============================================================


def report(function):


    result=analyze(
        function
    )



    print()


    print(
        "🔥 JARVIS IMPACT ANALYSIS v3.2"
    )


    print(
        "="*60
    )



    if "error" in result:

        print(
            result["error"]
        )

        return



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



    deps=sorted(

        result["dependencies"],

        key=lambda x:

            dependency_priority(x),

        reverse=True

    )



    for dep in deps:


        print(
            "↓",
            dep,
            "()"
        )



    original=find_function(
        function
    ).get(
        "calls",
        []
    )



    ignored=[

        x

        for x in original

        if x.lower()
        in IGNORE_FUNCTIONS

    ]



    if ignored:


        print(
            "\nIGNORED:"
        )


        for item in ignored:


            print(
                "×",
                item,
                "()"
            )



    print(
        "\nAFFECTED FILES:"
    )


    for file in result["files"]:


        print(
            "-",
            file
        )



    print()


    print(
        "CHANGE RISK:",
        result["risk"]
    )





# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    report(
        "speak_async"
    )