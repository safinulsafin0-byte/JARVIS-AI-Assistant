# ============================================================
# JARVIS DEPENDENCY GRAPH v2.2
# FILE AWARE CALL GRAPH ENGINE
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
# LOAD DATABASE
# ============================================================


def load_database():


    if not FUNCTION_DB.exists():

        print(
            "[ERROR] function_index missing"
        )

        return {}



    data = json.loads(

        FUNCTION_DB.read_text(
            encoding="utf-8"
        )

    )



    database = {}



    # dictionary format

    if isinstance(data,dict):


        for key,value in data.items():


            if isinstance(value,dict):

                database[key]=value



    # list format

    elif isinstance(data,list):


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
# CREATE FULL FUNCTION ID
# ============================================================


def full_name(data):


    file=data.get(
        "file",
        ""
    )


    function=data.get(
        "function",
        ""
    )



    module=file.replace(
        ".py",
        ""
    )


    return (
        module
        +
        "."
        +
        function
    )





# ============================================================
# BUILD GRAPH
# ============================================================


def build_graph():



    database=load_database()



    graph={}



    for name,data in database.items():


        node=full_name(
            data
        )


        graph[node]={

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


            "calls":[]


        }



    # resolve calls

    for name,data in database.items():


        source=full_name(
            data
        )


        for call in data.get(
            "calls",
            []
        ):



            for target,target_data in database.items():


                if target.lower()==call.lower():


                    graph[source]["calls"].append(

                        full_name(
                            target_data
                        )

                    )



    return graph





# ============================================================
# TRACE FLOW
# ============================================================


def trace(
        function,
        depth=3
):


    graph=build_graph()


    result=[]


    visited=set()



    def walk(node,level):


        if level>depth:

            return



        if node in visited:

            return



        visited.add(node)



        if node not in graph:

            return



        result.append(

            {

            "level":level,

            "node":node,

            "file":
                graph[node]["file"],


            }

        )



        for child in graph[node]["calls"]:


            walk(
                child,
                level+1
            )



    # search function


    start=None


    for node in graph:


        if node.endswith(
            "."+function
        ):

            start=node
            break



    if start:

        walk(
            start,
            0
        )



    return result





# ============================================================
# IMPACT ANALYSIS
# ============================================================


def impact(function):


    graph=build_graph()


    target=None



    for node in graph:


        if node.endswith(
            "."+function
        ):

            target=node



    affected=[]



    if not target:

        return []



    for node,data in graph.items():


        if target in data["calls"]:

            affected.append(
                node
            )


    return affected





# ============================================================
# PRINT
# ============================================================


def show(function):


    print()

    print(
        "🔥 JARVIS FILE AWARE GRAPH"
    )

    print(
        "="*60
    )



    flow=trace(
        function
    )



    for item in flow:


        print(

            "   "
            *
            item["level"]

            +

            "↓ "

            +

            item["node"]

            +

            " ["

            +

            item["file"]

            +

            "]"

        )



    print()


    print(
        "IMPACT:"
    )


    for x in impact(function):

        print(
            "↑",
            x
        )





# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    show(
        "speak_async"
    )