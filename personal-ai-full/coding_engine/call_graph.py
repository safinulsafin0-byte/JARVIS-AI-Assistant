# ============================================================
# JARVIS CALL GRAPH ENGINE v2.1
# BEASTMODE PROJECT FUNCTION GRAPH
# COPILOT STYLE CODE INTELLIGENCE
# ============================================================


from pathlib import Path
import json



# ============================================================
# PATH
# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent


GRAPH_FILE = (
    BASE_DIR
    /
    "memory"
    /
    "code_graph.json"
)





# ============================================================
# CONFIGURATION
# ============================================================


IGNORE_FUNCTIONS = {


    # logging
    "log",
    "logger",


    # helpers
    "clean_text",
    "model_exists",


    # common utils
    "validate",
    "check",
    "load",
    "save"

}





# ============================================================
# LOAD DATABASE
# ============================================================


def load_database():


    if not GRAPH_FILE.exists():

        raise FileNotFoundError(
            "code_graph.json not found"
        )


    return json.loads(

        GRAPH_FILE.read_text(
            encoding="utf-8"
        )

    )







# ============================================================
# BUILD PROJECT FUNCTION INDEX
# ============================================================


def build_function_index(data):


    functions = set()



    for file in data:


        for func in file.get(
            "functions",
            []
        ):


            functions.add(

                func["name"]

            )



    return functions








# ============================================================
# BUILD CLEAN GRAPH
# ============================================================


def build_call_graph():


    data = load_database()


    project_functions = build_function_index(
        data
    )


    graph = {}



    for file in data:


        filename = file["file"]



        for func in file.get(
            "functions",
            []
        ):


            name = func["name"]



            # ignore private functions

            if name.startswith("_"):

                continue



            calls = []



            for call in func.get(
                "calls",
                []
            ):



                # ignore private calls

                if call.startswith("_"):

                    continue



                # ignore utility

                if call in IGNORE_FUNCTIONS:

                    continue



                # only project functions

                if call in project_functions:


                    calls.append(
                        call
                    )



            graph[name] = {


                "file":
                    filename,


                "calls":
                    sorted(
                        list(
                            set(calls)
                        )
                    )

            }



    return graph







# ============================================================
# FIND FUNCTION
# ============================================================


def find_function(name):


    graph = build_call_graph()


    result = []



    for func,info in graph.items():


        if name.lower() in func.lower():


            result.append(

                {

                "function":
                    func,


                "file":
                    info["file"],


                "calls":
                    info["calls"]

                }

            )



    return result







# ============================================================
# TRACE EXECUTION FLOW
# ============================================================


def trace(start, depth=5):


    graph = build_call_graph()


    visited=set()



    print()

    print(
        "🔥 CLEAN CALL GRAPH:"
    )

    print(start)



    def walk(node,level):


        if level > depth:

            return



        if node in visited:

            return



        visited.add(node)



        for child in graph.get(
            node,
            {}
        ).get(
            "calls",
            []
        ):



            print(

                "   "
                *
                level

                +

                "↓ "

                +

                child

            )



            walk(

                child,

                level+1

            )



    walk(

        start,

        1

    )







# ============================================================
# PRINT ALL GRAPH
# ============================================================


def show_graph():


    graph = build_call_graph()



    print()


    print(
        "🔥 PROJECT CALL GRAPH"
    )



    for func,info in graph.items():


        print()

        print(
            func
        )


        for call in info["calls"]:


            print(
                "   ↓",
                call
            )







# ============================================================
# RUN
# ============================================================


if __name__ == "__main__":


    trace(

        "speak_api",

        depth=5

    )