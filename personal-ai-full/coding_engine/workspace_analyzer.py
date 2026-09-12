# ======================================
# JARVIS WORKSPACE ANALYZER v1
# PROJECT UNDERSTANDING ENGINE
# ======================================


import os
import json
from pathlib import Path



# ======================================
# CONFIG
# ======================================


PROJECT_ROOT = Path(
    r"D:\personal-ai-full"
)


IGNORE_DIRS = {

    "venv",
    "__pycache__",
    ".git",
    "models",
    "chroma"

}


SUPPORTED_EXTENSIONS = {

    ".py",
    ".js",
    ".ts",
    ".json",
    ".html",
    ".css",
    ".md"

}





# ======================================
# SCAN FILES
# ======================================


def scan_workspace():


    files = []


    for root, dirs, filenames in os.walk(
        PROJECT_ROOT
    ):


        # remove ignored folders

        dirs[:] = [

            d for d in dirs

            if d not in IGNORE_DIRS

        ]



        for file in filenames:


            path = Path(root) / file


            if path.suffix.lower() in SUPPORTED_EXTENSIONS:


                relative = path.relative_to(
                    PROJECT_ROOT
                )


                files.append(

                    str(relative)

                )


    return files









# ======================================
# LANGUAGE COUNT
# ======================================


def analyze_languages(files):


    languages = {

        "Python":0,
        "JavaScript":0,
        "TypeScript":0,
        "HTML":0,
        "CSS":0,
        "JSON":0,
        "Markdown":0

    }



    for file in files:


        ext = Path(file).suffix.lower()



        if ext == ".py":

            languages["Python"] += 1


        elif ext == ".js":

            languages["JavaScript"] += 1


        elif ext == ".ts":

            languages["TypeScript"] += 1


        elif ext == ".html":

            languages["HTML"] += 1


        elif ext == ".css":

            languages["CSS"] += 1


        elif ext == ".json":

            languages["JSON"] += 1


        elif ext == ".md":

            languages["Markdown"] += 1



    return languages









# ======================================
# IMPORTANT FILE DETECTOR
# ======================================


def find_main_files(files):


    important = [

        "main.py",
        "api_server.py",
        "config.py",
        "requirements.txt",
        "package.json"

    ]


    found = []


    for file in files:


        name = Path(file).name


        if name in important:

            found.append(file)



    return found









# ======================================
# READ FILE CONTEXT
# ======================================


def read_file_context(
    filename,
    max_lines=80
):


    file_path = (
        PROJECT_ROOT /
        filename
    )


    if not file_path.exists():

        return ""



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


    except:


        return ""











# ======================================
# CREATE WORKSPACE SUMMARY
# ======================================


def analyze_workspace():


    files = scan_workspace()


    result = {


        "project":

        PROJECT_ROOT.name,


        "total_files":

        len(files),



        "languages":

        analyze_languages(files),



        "main_files":

        find_main_files(files),



        "files":

        files[:200]

    }



    return result









# ======================================
# SAVE MEMORY
# ======================================


def save_workspace():


    data = analyze_workspace()


    output = (

        PROJECT_ROOT /

        "memory" /

        "workspace.json"

    )


    output.parent.mkdir(
        exist_ok=True
    )


    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            data,

            f,

            indent=4

        )



    return data









# ======================================
# TEST
# ======================================


if __name__ == "__main__":


    print(
        "🔥 JARVIS WORKSPACE ANALYZER STARTED"
    )


    result = save_workspace()



    print(
        json.dumps(
            result,
            indent=4
        )
    )