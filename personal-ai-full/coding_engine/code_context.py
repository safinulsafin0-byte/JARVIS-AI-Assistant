# ======================================
# JARVIS CODE CONTEXT ENGINE v1
# PROJECT CODE RETRIEVAL
# ======================================


from pathlib import Path


PROJECT_ROOT = Path(
    r"D:\personal-ai-full"
)



def get_file_content(
    filename,
    max_lines=200
):

    file_path = PROJECT_ROOT / filename


    if not file_path.exists():

        return "File not found"



    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            lines = f.readlines()


        return "".join(
            lines[:max_lines]
        )


    except Exception as e:

        return str(e)





def build_context(files):


    context = ""


    for file in files:


        context += f"""

=========================
FILE: {file}
=========================


"""


        context += get_file_content(
            file
        )


        context += "\n\n"



    return context





if __name__ == "__main__":


    print(
        "🔥 CODE CONTEXT ENGINE"
    )


    ctx = build_context(

        [
            "api_server.py",
            "main.py"
        ]

    )


    print(
        ctx[:3000]
    )