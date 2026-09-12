# ============================================================
# JARVIS DEPENDENCY RESOLVER v7.3
#
# Missing Dependency Repair Engine
#
# AST + Function Index + Call Graph Aware
#
# ============================================================


import json
import ast
from pathlib import Path





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
# LOAD DATABASE
# ============================================================


def load_functions():


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
# EXTRACT GENERATED CALLS
# ============================================================


def extract_calls(code):


    calls=[]


    tree=ast.parse(code)



    for node in ast.walk(tree):


        if isinstance(node,ast.Call):


            if isinstance(

                node.func,

                ast.Name

            ):

                calls.append(

                    node.func.id

                )



            elif isinstance(

                node.func,

                ast.Attribute

            ):

                calls.append(

                    node.func.attr

                )



    return list(set(calls))







# ============================================================
# REPLACEMENT KNOWLEDGE
# ============================================================


KNOWN_REPLACEMENTS = {


    "create_streaming_wav":

        "generate_wav",


    "start_stream":

        "threading.Thread",


    "stream_play":

        "winsound.PlaySound"


}







# ============================================================
# RESOLVER
# ============================================================


def resolve_dependencies(code):


    database = load_functions()


    calls = extract_calls(code)



    available=set(

        database.keys()

    )



    repairs=[]

    unresolved=[]



    for call in calls:


        if call in available:

            continue



        if call in KNOWN_REPLACEMENTS:


            replacement = KNOWN_REPLACEMENTS[call]


            repairs.append(

                {

                "missing":call,

                "replacement":replacement

                }

            )


        else:


            unresolved.append(call)





    return {


        "repairs":repairs,

        "unresolved":unresolved,

        "safe":

            len(unresolved)==0

    }









# ============================================================
# APPLY REPAIR PLAN
# ============================================================


def apply_repairs(code,result):


    repaired=code



    for item in result["repairs"]:


        old=item["missing"]

        new=item["replacement"]



        repaired=repaired.replace(

            old,

            new

        )



    return repaired







# ============================================================
# REPORT
# ============================================================


def print_report(result):


    print()

    print(

        "🔥 JARVIS DEPENDENCY RESOLVER v7.3"

    )

    print(

        "="*60

    )


    print()



    print(

        "REPLACEMENTS FOUND:"

    )


    for item in result["repairs"]:


        print(

            "✓",

            item["missing"],

            "→",

            item["replacement"]

        )





    print()


    print(

        "UNRESOLVED:"

    )


    if result["unresolved"]:


        for x in result["unresolved"]:

            print(

                "❌",

                x

            )


    else:

        print(

            "None"

        )



    print()


    if result["safe"]:


        print(

            "RESULT: ✓ PATCH REPAIR READY"

        )

    else:


        print(

            "RESULT: ⚠️ MANUAL REVIEW REQUIRED"

        )









# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    generated_code="""


def speak_async(text):

    cleaned=clean_text(text)

    temp=create_streaming_wav(cleaned)

    start_stream(temp)

    return {

        "success":True

    }

"""



    result=resolve_dependencies(

        generated_code

    )


    print_report(

        result

    )


    if result["safe"]:


        print()

        print(

            "REPAIRED CODE:"

        )


        print(

            apply_repairs(

                generated_code,

                result

            )

        )