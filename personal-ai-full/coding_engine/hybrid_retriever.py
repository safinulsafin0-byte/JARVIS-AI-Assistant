# ============================================================
# JARVIS HYBRID RETRIEVER v3.0
# BEASTMODE COPILOT ENGINE
#
# FUNCTION INDEX
# CALL GRAPH
# RAG SEARCH
# API FLOW AWARE
# ============================================================


import json
import re
from pathlib import Path


from rag.retriever import search as rag_search



# ============================================================
# PATH
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


def load_functions():


    if not FUNCTION_DB.exists():

        print(
            "[HYBRID] function database missing"
        )

        return {}



    try:

        data = json.loads(

            FUNCTION_DB.read_text(
                encoding="utf-8"
            )

        )


        # support list json

        if isinstance(data,list):

            return {

                x.get("function"):x

                for x in data

                if x.get("function")

            }



        return data



    except Exception as e:


        print(
            "[HYBRID LOAD ERROR]",
            e
        )


        return {}







# ============================================================
# QUERY PARSER
# ============================================================


def extract_symbols(query):


    words = re.findall(

        r"[a-zA-Z_][a-zA-Z0-9_]*",

        query.lower()

    )


    ignore={

        "how",
        "does",
        "what",
        "why",
        "where",
        "when",

        "use",
        "using",

        "from",
        "with",

        "the",
        "and",

        "file",
        "code",

        "python",
        "voice",
        "tts",

        "api"

    }



    result=[]



    for w in words:


        if w in ignore:
            continue


        if len(w)<3:
            continue


        result.append(w)



    return list(
        dict.fromkeys(result)
    )






def extract_files(query):


    return re.findall(

        r"[a-zA-Z0-9_-]+\.py",

        query.lower()

    )








# ============================================================
# FUNCTION RANKING ENGINE
# ============================================================


def search_functions(

        query,

        limit=5

):


    database=load_functions()


    symbols=extract_symbols(query)

    files=extract_files(query)



    ranked=[]



    for name,data in database.items():


        # remove useless nodes

        if data.get("type")=="module_header":

            continue



        score=0



        fname=name.lower()


        file=data.get(
            "file",
            ""
        ).lower()



        role=data.get(
            "role",
            ""
        ).lower()



        calls=" ".join(

            data.get(
                "calls",
                []
            )

        ).lower()





        # -----------------------------
        # Exact function
        # -----------------------------


        for s in symbols:


            if s==fname:

                score+=600


            elif s in fname:

                score+=120





        # -----------------------------
        # Filename
        # -----------------------------


        for f in files:


            clean=f.replace(
                ".py",
                ""
            )


            if clean in file:

                score+=350






        # -----------------------------
        # API priority
        # -----------------------------


        if "api endpoint" in role:

            score+=500





        # -----------------------------
        # Call relation
        # -----------------------------


        for s in symbols:


            if s in calls:

                score+=300






        # -----------------------------
        # Voice relation
        # -----------------------------


        if (
            "speak_async" in query.lower()
            and
            "speak_async" in calls
        ):

            score+=400





        if score>0:


            ranked.append(

                {

                "score":score,

                "data":data

                }

            )





    ranked.sort(

        key=lambda x:x["score"],

        reverse=True

    )



    return ranked[:limit]







# ============================================================
# CALL GRAPH EXPANDER
# ============================================================


def expand_calls(

        root,

        depth=3,

        max_nodes=12

):


    database=load_functions()



    result=[]

    visited=set()



    def walk(name,level):


        if level>depth:
            return


        if len(result)>=max_nodes:
            return


        if name in visited:
            return



        visited.add(name)



        if name not in database:

            return



        node=database[name]


        result.append(node)



        for child in node.get(

            "calls",

            []

        ):


            walk(

                child,

                level+1

            )




    walk(

        root.get("function"),

        0

    )



    return result







# ============================================================
# HYBRID CONTEXT BUILDER
# ============================================================


def hybrid_search(

        query,

        max_chars=16000

):


    context=[]



    functions=search_functions(

        query,

        limit=3

    )





    print()

    print(
        "[HYBRID] Root functions:",
        len(functions)
    )




    for item in functions:


        root=item["data"]



        chain=expand_calls(

            root

        )



        for node in chain:


            block=f"""

==================================================
FUNCTION GRAPH
==================================================


FUNCTION:
{node.get("function")}


FILE:
{node.get("file")}


PATH:
{node.get("path")}


LINE:
{node.get("line")}


ROLE:
{node.get("role")}


CALLS:
{node.get("calls")}



"""


            context.append(block)







    # -----------------------------
    # RAG
    # -----------------------------


    rag=rag_search(

        query,

        n=5

    )



    if rag:


        context.append(

f"""

==================================================
SEMANTIC CODE SEARCH
==================================================


{rag}

"""

        )





    final="\n".join(context)



    print(

        "[HYBRID] Context chars:",

        len(final)

    )



    return final[:max_chars]







# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    output=hybrid_search(

        "How does api_server.py use speak_async from voice.tts?"

    )


    print(output)