# ============================================================
# JARVIS CODE INTELLIGENCE ENGINE v1
# FUNCTION KNOWLEDGE DATABASE
# ============================================================


import json
from pathlib import Path


# ============================================================
# PATHS
# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent


GRAPH_FILE = (
    BASE_DIR
    /
    "memory"
    /
    "code_graph.json"
)


OUTPUT_FILE = (
    BASE_DIR
    /
    "memory"
    /
    "function_index.json"
)



# ============================================================
# LOAD AST DATABASE
# ============================================================


def load_graph():

    if not GRAPH_FILE.exists():

        raise FileNotFoundError(
            "code_graph.json missing"
        )


    return json.loads(
        GRAPH_FILE.read_text(
            encoding="utf-8"
        )
    )





# ============================================================
# BUILD FUNCTION INDEX
# ============================================================


def build_function_index(data):


    index = {}



    # ----------------------------------
    # Collect functions
    # ----------------------------------

    for file_data in data:


        file_path = file_data["file"]


        filename = Path(
            file_path
        ).name



        imports = file_data.get(
            "imports",
            []
        )



        for func in file_data.get(
            "functions",
            []
        ):


            name = func["name"]



            index[name] = {


                "function":
                    name,


                "file":
                    filename,


                "path":
                    file_path,


                "line":
                    func.get(
                        "line",
                        0
                    ),


                "type":
                    func.get(
                        "type",
                        "function"
                    ),



                "calls":
                    func.get(
                        "calls",
                        []
                    ),



                "imports":
                    imports,


                "called_by":[]

            }



    return index







# ============================================================
# BUILD REVERSE CALL GRAPH
# ============================================================


def add_callers(index):


    for func,info in index.items():


        for child in info["calls"]:


            if child in index:


                index[child][
                    "called_by"
                ].append(
                    func
                )





# ============================================================
# ROLE DETECTOR
# ============================================================


def detect_role(info):


    name = info["function"].lower()

    file = info["file"].lower()



    if "api" in name:

        return "API endpoint"



    if "route" in info["calls"]:

        return "Web route"



    if "voice" in file:

        return "Voice system"



    if "memory" in file:

        return "Memory system"



    if "rag" in file:

        return "RAG system"



    if "agent" in file:

        return "Agent logic"



    return "General function"






# ============================================================
# SAVE
# ============================================================


def build_intelligence():


    print(
        "\n🔥 JARVIS CODE INTELLIGENCE STARTED\n"
    )


    graph = load_graph()


    index = build_function_index(
        graph
    )


    add_callers(
        index
    )



    for name,data in index.items():

        data["role"] = detect_role(
            data
        )



    OUTPUT_FILE.write_text(

        json.dumps(
            index,
            indent=4
        ),

        encoding="utf-8"

    )



    print(
        "✅ FUNCTION DATABASE CREATED"
    )


    print(
        OUTPUT_FILE
    )


    print(
        "Functions:",
        len(index)
    )


    return index






# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":


    data = build_intelligence()


    print("\nExample:\n")


    print(
        json.dumps(
            data.get(
                "speak_api"
            ),
            indent=4
        )
    )