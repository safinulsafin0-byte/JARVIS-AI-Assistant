# ======================================
# JARVIS CODING AGENT v2
# PROJECT AWARE COPILOT MODE
# ======================================


from llm.ollama_client import chat
from coding_engine.code_context import build_context



SYSTEM = """

You are JARVIS Coding Assistant.

You are working inside a real software project.

Your responsibilities:

- Understand project architecture
- Explain code
- Debug errors
- Suggest improvements
- Refactor safely
- Generate production quality code

Always consider the provided project context.

Do not give random solutions.
Respect existing architecture.

"""





def ask_jarvis_code(

    task,

    files=None,

    code="",

    language=""

):


    if files is None:

        files = []



    project_context = ""


    if files:

        project_context = build_context(
            files
        )



    prompt = f"""

USER TASK:

{task}


PROGRAMMING LANGUAGE:

{language}



PROJECT CONTEXT:

{project_context}



CURRENT CODE:

{code}



Analyze the problem and provide the best solution.

"""



    messages = [

        {
            "role":"system",
            "content":SYSTEM
        },

        {
            "role":"user",
            "content":prompt
        }

    ]



    return chat(
        messages
    )







if __name__ == "__main__":


    response = ask_jarvis_code(

        task="Explain my API architecture",

        files=[

            "api_server.py",

            "main.py",

            "agent/jarvis_event_receiver.py"

        ]

    )


    print(response)