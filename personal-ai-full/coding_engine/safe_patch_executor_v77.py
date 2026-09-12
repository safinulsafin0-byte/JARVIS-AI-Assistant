# ============================================================
# JARVIS SAFE PATCH EXECUTOR v7.7
#
# FINAL EXECUTION ENGINE
#
# Features:
# - Automatic backup
# - Safe patch apply
# - AST validation
# - Rollback on failure
#
# ============================================================


from pathlib import Path
import ast
import shutil
import datetime





# ============================================================
# BACKUP SYSTEM
# ============================================================


def create_backup(file_path):


    file_path = Path(file_path)


    if not file_path.exists():

        return None



    backup_dir = (

        file_path.parent.parent

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

        file_path.stem

        +

        "_backup_"

        +

        timestamp

        +

        file_path.suffix

    )



    shutil.copy2(

        file_path,

        backup

    )



    return backup







# ============================================================
# AST VALIDATION
# ============================================================


def validate_python(code):


    try:


        ast.parse(code)


        compile(

            code,

            "<patch>",

            "exec"

        )


        return True,None



    except Exception as e:


        return False,str(e)









# ============================================================
# FUNCTION FINDER
# ============================================================


def find_function_range(

        source,

        function_name

):


    tree = ast.parse(source)



    for node in ast.walk(tree):


        if isinstance(

            node,

            ast.FunctionDef

        ):


            if node.name == function_name:


                return (

                    node.lineno-1,

                    node.end_lineno

                )



    return None,None







# ============================================================
# APPLY FUNCTION PATCH
# ============================================================


def apply_function_patch(

        file_path,

        function_name,

        new_function

):


    file_path = Path(file_path)



    if not file_path.exists():

        return {


            "success":False,

            "error":
            "File not found"

        }





    # Backup first

    backup = create_backup(

        file_path

    )



    if not backup:


        return {


            "success":False,

            "error":
            "Backup failed"

        }





    old_source = file_path.read_text(

        encoding="utf-8"

    )





    start,end = find_function_range(

        old_source,

        function_name

    )





    if start is None:


        return {


            "success":False,

            "error":
            "Function not found"

        }





    lines = old_source.splitlines()





    updated_lines = (

        lines[:start]

        +

        new_function.splitlines()

        +

        lines[end:]

    )





    new_source = "\n".join(

        updated_lines

    )





    valid,error = validate_python(

        new_source

    )





    if not valid:


        # rollback

        shutil.copy2(

            backup,

            file_path

        )


        return {


            "success":False,

            "error":
            error,


            "rollback":
            True

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
# REPORT
# ============================================================


def print_report(result):


    print()


    print(

        "🔥 JARVIS SAFE PATCH EXECUTOR v7.7"

    )


    print(

        "="*60

    )


    print()



    if result["success"]:


        print(

            "PATCH STATUS:"

        )


        print(

            "✓ BACKUP CREATED"

        )


        print(

            "✓ PATCH APPLIED"

        )


        print(

            "✓ AST VALIDATION PASSED"

        )


        print()


        print(

            "RESULT: ✅ PATCH SUCCESSFUL"

        )


        print()


        print(

            "BACKUP:",

            result["backup"]

        )



    else:


        print(

            "PATCH FAILED"

        )


        print(

            result["error"]

        )



        if result.get("rollback"):

            print(

                "✓ ROLLBACK COMPLETED"

            )









# ============================================================
# TEST
# ============================================================


if __name__=="__main__":


    print()


    print(

        "🔥 JARVIS SAFE PATCH EXECUTOR v7.7"

    )


    print(

        "="*60

    )


    print()


    print(

        "READY"

    )


    print()


    print(

        "Capabilities:"

    )


    print(

        "✓ Backup"

    )


    print(

        "✓ Function replacement"

    )


    print(

        "✓ AST validation"

    )


    print(

        "✓ Rollback"

    )