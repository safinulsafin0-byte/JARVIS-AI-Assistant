# ======================================
# JARVIS RAG CODING AGENT v2
# COPILOT STYLE CODE RETRIEVAL
# GROUNDED CODE ASSISTANT
# ======================================


from llm.ollama_client import chat

from rag.retriever import search





# ======================================
# SYSTEM PROMPT
# ======================================


SYSTEM = """

You are JARVIS Coding Assistant.

You are an AI coding assistant for an existing software project.

You have access to retrieved project source code.

STRICT RULES:

1. Answer ONLY using the provided project context.

2. Do NOT invent files, functions, APIs, or libraries.

3. Do NOT suggest replacing the current architecture unless the user asks.

4. Do NOT provide generic tutorials when project code exists.

5. Explain the existing implementation first.

6. When mentioning code, always mention:
   - file name
   - function name
   - purpose

7. If the answer is not present in the context, say:
   "This information is not available in the provided project code."

8. For debugging:
   - identify the issue
   - explain the cause
   - provide the smallest fix


You are JARVIS. Be precise and technical.

"""





# ======================================
# CODE AGENT
# ======================================


def ask_code_agent(query):


    print()

    print(
        "🧠 JARVIS CODE QUERY:"
    )

    print(query)

    print()



    # Retrieve project context

    context = search(

        query,

        n=7

    )



    if not context:


        return (

            "I could not find relevant code "

            "inside the project."

        )





    prompt = f"""

User Request:

{query}



Retrieved Project Context:

==================================================

{context}

==================================================



Instructions:

Analyze the provided project code.

Explain the existing implementation.

Do not create new code unless requested.

Answer with file names and functions when possible.



Response:

"""





    messages = [


        {

            "role": "system",

            "content": SYSTEM

        },


        {

            "role": "user",

            "content": prompt

        }


    ]





    return chat(

        messages

    )







# ======================================
# TEST
# ======================================


if __name__ == "__main__":



    query = (

        "How does api_server.py implement "

        "voice output using voice.tts "

        "and speak_async?"

    )



    result = ask_code_agent(

        query

    )



    print()

    print(

        "🤖 JARVIS RESPONSE:"

    )

    print()

    print(result)