# ============================================================
# JARVIS AST REWRITE ENGINE v7.5
#
# SAFE FUNCTION LEVEL CODE REPLACEMENT
#
# ============================================================


import ast
from pathlib import Path
import shutil
import datetime





# ============================================================
# BACKUP
# ============================================================


def create_backup(file):


    file = Path(file)


    backup_dir = (

        file.parent.parent

        /

        "memory"

        /

        "patch_backups"

    )


    backup_dir.mkdir(

        parents=True,

        exist_ok=True

    )


    timestamp = datetime.datetime.now().strftime(

        "%Y%m%d_%H%M%S"

    )


    backup = backup_dir / (

        file.stem

        +

        "_"

        +

        timestamp

        +

        file.suffix

    )


    shutil.copy2(

        file,

        backup

    )


    return backup







# ============================================================
# FIND FUNCTION RANGE
# ============================================================


def find_function_node(

        tree,

        function_name

):


    for node in ast.walk(tree):


        if isinstance(

            node,

            ast.FunctionDef

        ):


            if node.name == function_name:

                return node



    return None









# ============================================================
# FUNCTION REPLACER
# ============================================================


def replace_function(

        file_path,

        function_name,

        new_code

):


    file_path = Path(file_path)



    source = file_path.read_text(

        encoding="utf-8"

    )


    tree = ast.parse(

        source

    )



    target = find_function_node(

        tree,

        function_name

    )


    if not target:

        return {

            "success":False,

            "error":
            "Function not found"

        }





    # backup

    backup = create_backup(

        file_path

    )





    lines = source.splitlines()





    start = target.lineno - 1


    end = target.end_lineno





    new_lines = new_code.splitlines()





    updated = (

        lines[:start]

        +

        new_lines

        +

        lines[end:]

    )





    new_source = "\n".join(

        updated

    )





    # validation

    try:


        ast.parse(

            new_source

        )


    except Exception as e:


        return {


            "success":False,

            "error":
            str(e)

        }





    file_path.write_text(

        new_source,

        encoding="utf-8"

    )




    return {


        "success":True,

        "backup":

        str(backup)

    }









# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    print(

        """

🔥 JARVIS AST REWRITE ENGINE v7.5

READY

Capabilities:

✓ Function detection
✓ Backup creation
✓ Function replacement
✓ AST validation

"""

    )