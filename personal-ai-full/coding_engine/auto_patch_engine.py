# ============================================================
# JARVIS AUTO PATCH ENGINE v6.1
# SAFE CODE MODIFICATION SYSTEM
#
# Patch Generator + Diff Engine + Safety Validator
# ============================================================


from pathlib import Path
import difflib
import shutil
import datetime
import re


from coding_engine.patch_generator import (
    generate_patch_plan
)





# ============================================================
# PATH
# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent





# ============================================================
# BACKUP SYSTEM
# ============================================================


def create_backup(file):


    file = Path(file)


    if not file.exists():

        return None



    backup_dir = (

        BASE_DIR
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



    backup = (

        backup_dir
        /
        f"{file.stem}_{timestamp}{file.suffix}"

    )



    shutil.copy2(

        file,

        backup

    )


    return backup





# ============================================================
# DIFF GENERATOR
# ============================================================


def generate_diff(

        old,

        new,

        filename

):


    diff = difflib.unified_diff(

        old.splitlines(),

        new.splitlines(),

        fromfile=

            filename + " (OLD)",


        tofile=

            filename + " (NEW)",


        lineterm=""

    )


    return "\n".join(diff)









# ============================================================
# PATCH SAFETY VALIDATOR
# ============================================================


def validate_patch(

        old_code,

        new_code,

        dependencies

):


    warnings = []


    old_lower = old_code.lower()

    new_lower = new_code.lower()



    # ---------------------------------
    # Dependency removal detection
    # ---------------------------------


    for dep in dependencies:


        dep = dep.lower()



        if dep in old_lower and dep not in new_lower:


            warnings.append(

                f"Removed dependency: {dep}()"

            )





    # ---------------------------------
    # Critical TTS protection example
    # ---------------------------------


    critical = [

        "generate_wav",

        "stop",

        "play",

        "thread"

    ]



    for item in critical:


        if item in old_lower and item not in new_lower:


            warnings.append(

                f"Critical functionality removed: {item}"

            )





    # ---------------------------------
    # Return contract check
    # ---------------------------------


    old_returns = re.findall(

        r'"([^"]+)"\s*:',

        old_code

    )



    new_returns = re.findall(

        r'"([^"]+)"\s*:',

        new_code

    )



    missing = set(old_returns) - set(new_returns)



    for key in missing:


        warnings.append(

            f"Return field removed: {key}"

        )





    safe = len(warnings) == 0



    return {


        "safe":

            safe,


        "warnings":

            warnings

    }









# ============================================================
# PATCH PROPOSAL
# ============================================================


def create_patch(

        function,

        request,

        new_code

):


    plan = generate_patch_plan(

        function,

        request

    )



    if "error" in plan:


        return plan





    old_code = plan.get(

        "current_code",

        ""

    )



    validation = validate_patch(

        old_code,

        new_code,

        plan.get(

            "dependencies",

            []

        )

    )





    diff = generate_diff(

        old_code,

        new_code,

        plan["target"]["file"]

    )





    return {


        "target":

            plan["target"],



        "risk":

            plan["risk"],



        "diff":

            diff,



        "validation":

            validation,



        "backup_required":

            True,



        "affected_files":

            plan["files"]

    }









# ============================================================
# APPLY PATCH
# ============================================================


def apply_patch(

        file,

        new_content

):


    backup = create_backup(

        file

    )



    if not backup:


        print(

            "❌ Backup failed"

        )


        return False





    Path(file).write_text(

        new_content,

        encoding="utf-8"

    )



    print(

        "✅ PATCH APPLIED"

    )


    print(

        "BACKUP:",

        backup

    )


    return True









# ============================================================
# REPORT
# ============================================================


def print_patch(

        function,

        request,

        new_code

):


    result = create_patch(

        function,

        request,

        new_code

    )



    print()

    print(

        "🔥 JARVIS AUTO PATCH ENGINE v6.1"

    )

    print(

        "="*60

    )



    if "error" in result:


        print(

            result["error"]

        )

        return





    target = result["target"]



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

        "\nRISK:",

        result["risk"]

    )





    print(

        "\nVALIDATION:"

    )



    validation = result["validation"]



    if validation["safe"]:


        print(

            "✅ PATCH SAFE"

        )


    else:


        print(

            "⚠️ PATCH BLOCKED"

        )



        for warning in validation["warnings"]:


            print(

                " -",

                warning

            )





    print(

        "\nAFFECTED FILES:"

    )


    for f in result["affected_files"]:


        print(

            "-",

            f

        )





    print(

        "\nGENERATED DIFF:"

    )


    print(

        result["diff"]

    )





    print(

        "\nBACKUP REQUIRED:",

        result["backup_required"]

    )







# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":



    example_new_code = """

def speak_async(text):

    return {

        "success": True,

        "streaming": True

    }

"""



    print_patch(

        "speak_async",

        "Replace speak_async with streaming TTS support",

        example_new_code

    )