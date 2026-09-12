# ============================================================
# JARVIS AST ANALYZER v2
# CODE STRUCTURE INTELLIGENCE ENGINE
# COPILOT STYLE FUNCTION GRAPH BUILDER
# ============================================================


import ast
from pathlib import Path
import json



# ============================================================
# CONFIG
# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent


IGNORE = {

    "venv",
    "__pycache__",
    ".git",
    "node_modules"

}



# Python built-in / common noise

IGNORE_CALLS = {


    # builtins
    "print",
    "str",
    "int",
    "float",
    "bool",
    "len",
    "list",
    "dict",
    "set",
    "tuple",
    "range",
    "open",
    "super",
    "isinstance",
    "type",

    # object methods
    "append",
    "extend",
    "insert",
    "remove",
    "pop",

    # string methods
    "strip",
    "replace",
    "split",
    "join",
    "lower",
    "upper",
    "format",

    # file/path
    "exists",
    "mkdir",
    "read_text",
    "write_text",

    # json
    "loads",
    "dumps",

    # flask/common
    "route",
    "get",
    "post",
    "jsonify"

}




# ============================================================
# EXTRACT FUNCTION CALL
# ============================================================


def extract_call_name(node):


    if isinstance(
        node.func,
        ast.Name
    ):

        return node.func.id



    elif isinstance(
        node.func,
        ast.Attribute
    ):

        return node.func.attr



    return None





# ============================================================
# PYTHON FILE ANALYZER
# ============================================================


def analyze_python_file(file_path):


    result = {


        "file": str(file_path),


        "functions": [],


        "classes": [],


        "imports": []

    }



    try:


        code = Path(file_path).read_text(

            encoding="utf-8",

            errors="ignore"

        )


        tree = ast.parse(code)



        # -------------------------
        # Imports
        # -------------------------


        for node in ast.walk(tree):


            if isinstance(
                node,
                ast.Import
            ):


                for item in node.names:

                    result["imports"].append(

                        item.name

                    )



            elif isinstance(
                node,
                ast.ImportFrom
            ):


                if node.module:

                    result["imports"].append(

                        node.module

                    )





        # -------------------------
        # Functions
        # -------------------------


        for node in ast.walk(tree):


            if isinstance(
                node,
                (ast.FunctionDef,
                 ast.AsyncFunctionDef)
            ):



                calls = []



                for child in ast.walk(node):


                    if isinstance(
                        child,
                        ast.Call
                    ):



                        name = extract_call_name(
                            child
                        )


                        if (

                            name

                            and

                            name not in IGNORE_CALLS

                        ):


                            calls.append(

                                name

                            )





                result["functions"].append(

                    {


                    "name":
                        node.name,


                    "line":
                        node.lineno,


                    "type":
                        "async_function"
                        if isinstance(
                            node,
                            ast.AsyncFunctionDef
                        )
                        else
                        "function",



                    "calls":
                        sorted(
                            list(
                                set(calls)
                            )
                        )

                    }


                )






        # -------------------------
        # Classes
        # -------------------------


        for node in ast.walk(tree):


            if isinstance(
                node,
                ast.ClassDef
            ):


                methods = []



                for child in node.body:


                    if isinstance(
                        child,
                        ast.FunctionDef
                    ):


                        methods.append(

                            child.name

                        )



                result["classes"].append(

                    {


                    "name":
                        node.name,


                    "line":
                        node.lineno,


                    "methods":
                        methods

                    }

                )





    except Exception as e:


        print(

            "AST ERROR:",

            file_path,

            e

        )



    return result






# ============================================================
# PROJECT SCANNER
# ============================================================


def scan_project(folder):


    database = []



    folder = Path(folder)



    for file in folder.rglob("*.py"):



        if any(

            x in file.parts

            for x in IGNORE

        ):

            continue




        print(

            "Analyzing:",

            file

        )



        database.append(

            analyze_python_file(
                file
            )

        )



    return database





# ============================================================
# SAVE DATABASE
# ============================================================


def build_ast_database():



    print(

        "\n🔥 JARVIS AST ANALYZER v2 STARTED\n"

    )



    data = scan_project(

        BASE_DIR

    )




    output = (

        BASE_DIR

        /

        "memory"

        /

        "code_graph.json"

    )




    output.write_text(

        json.dumps(

            data,

            indent=4

        ),

        encoding="utf-8"

    )




    print()

    print(

        "✅ AST DATABASE CREATED"

    )


    print(

        output

    )


    print(

        "Files:",

        len(data)

    )



    return data





# ============================================================
# RUN
# ============================================================


if __name__ == "__main__":


    build_ast_database()