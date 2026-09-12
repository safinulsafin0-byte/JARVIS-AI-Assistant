# ============================================================
# JARVIS CODE INTELLIGENCE v2.1
# DEPENDENCY + CALL GRAPH REASONING ENGINE
# ============================================================


import json
from pathlib import Path



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
# LOAD JSON
# ============================================================


def load_json(path):

    try:

        if not path.exists():

            print(
                "[ERROR] Missing:",
                path
            )

            return {}



        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )


    except Exception as e:

        print(
            "[JSON ERROR]",
            e
        )

        return {}





# ============================================================
# LOAD FUNCTION DATABASE
# ============================================================


def load_functions():


    data = load_json(
        FUNCTION_DB
    )


    database = {}



    # ------------------------------------
    # Dictionary format
    # ------------------------------------

    if isinstance(data, dict):


        for key,value in data.items():


            if not isinstance(
                value,
                dict
            ):
                continue



            name = value.get(
                "function",
                key
            )


            database[name] = value



        return database




    # ------------------------------------
    # List format
    # ------------------------------------


    if isinstance(data,list):


        for item in data:


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


    database = load_functions()


    target = name.lower()



    for func,data in database.items():


        if func.lower()==target:

            return data



    return None





# ============================================================
# FIND CALLERS
# ============================================================


def find_callers(target):


    database = load_functions()


    callers=[]


    for name,data in database.items():


        calls=data.get(
            "calls",
            []
        )


        for call in calls:


            if call.lower()==target.lower():

                callers.append(

                    {

                    "function":name,

                    "file":
                        data.get(
                            "file",
                            ""
                        ),

                    "line":
                        data.get(
                            "line",
                            ""
                        )

                    }

                )


    return callers





# ============================================================
# BUILD CALL TREE
# ============================================================


def build_call_chain(
        function,
        depth=3
):


    database=load_functions()


    result=[]


    visited=set()



    def walk(name,level):


        if level > depth:

            return



        if name in visited:

            return



        visited.add(name)



        if name not in database:

            return



        data=database[name]



        result.append(

            {

            "level":level,

            "function":name,

            "file":
                data.get(
                    "file",
                    ""
                ),

            "line":
                data.get(
                    "line",
                    ""
                ),

            "calls":
                data.get(
                    "calls",
                    []
                )

            }

        )




        for child in data.get(
            "calls",
            []
        ):


            walk(
                child,
                level+1
            )




    walk(
        function,
        0
    )


    return result





# ============================================================
# COMPLETE ANALYSIS
# ============================================================


def analyze_function(function):


    data=find_function(
        function
    )



    if not data:


        return {


            "error":
            f"{function} not found"


        }





    return {


        "function":
            function,


        "file":
            data.get(
                "file"
            ),


        "line":
            data.get(
                "line"
            ),


        "role":
            data.get(
                "role"
            ),


        "calls":
            build_call_chain(
                function
            ),


        "called_by":
            find_callers(
                function
            )

    }





# ============================================================
# PRINT EXPLANATION
# ============================================================


def explain(function):


    info=analyze_function(
        function
    )



    print()

    print(
        "🔥 JARVIS CODE REASONING"
    )

    print(
        "="*60
    )


    if "error" in info:

        print(
            info["error"]
        )

        return




    print(
        "FUNCTION:",
        info["function"]
    )


    print(
        "FILE:",
        info["file"]
    )


    print(
        "LINE:",
        info["line"]
    )


    print()



    print(
        "CALL FLOW:"
    )


    for item in info["calls"]:


        indent="   "*item["level"]


        print(

            indent
            +
            "↓ "
            +
            item["function"]
            +
            "  ["
            +
            str(item["file"])
            +
            "]"

        )





    print()


    print(
        "CALLED BY:"
    )


    if not info["called_by"]:

        print(
            "None"
        )


    else:


        for caller in info["called_by"]:


            print(

                "↑",

                caller["function"],

                "[",

                caller["file"],

                "]"

            )





# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    explain(
        "speak_async"
    )