# ======================================
# JARVIS CONTEXT ANALYZER AGENT v1
# USER ACTIVITY UNDERSTANDING ENGINE
# ======================================


import time
import requests
import json



EVENT_URL = "http://127.0.0.1:5002/event"



last_context = ""





# ======================================
# ANALYZE ACTIVITY
# ======================================


def analyze_context(activity):


    global last_context



    if not activity:

        return None



    activity_type = activity.get(

        "type",

        ""

    )



    message = activity.get(

        "message",

        ""

    ).lower()



    context = None

    response = None





    # ==============================
    # CODING
    # ==============================


    if (

        "github" in message

        or

        "code" in message

        or

        "visual studio" in message

        or

        "vscode" in message

    ):


        context = "coding"


        response = (

            "Coding activity detected."

        )







    # ==============================
    # RESEARCH
    # ==============================


    elif (

        "scholar" in message

        or

        "research" in message

        or

        "paper" in message

        or

        "google" in message

    ):


        context = "research"


        response = (

            "Research activity detected."

        )







    # ==============================
    # ENTERTAINMENT
    # ==============================


    elif (

        "youtube" in message

        or

        "netflix" in message

        or

        "movie" in message

    ):


        context = "entertainment"


        response = (

            "Entertainment activity detected."

        )







    # ==============================
    # AI USAGE
    # ==============================


    elif (

        "chatgpt" in message

        or

        "ai assistant" in message

    ):


        context = "ai_usage"


        response = (

            "AI assistant usage detected."

        )







    else:


        context = "browsing"


        response = (

            "General browsing detected."

        )







    # Avoid repeated alerts


    if context == last_context:


        return None





    last_context = context



    return {


        "type":

        "context_change",



        "context":

        context,



        "message":

        response

    }









# ======================================
# SEND TO JARVIS
# ======================================


def send_event(event):


    try:


        requests.post(

            EVENT_URL,

            json=event,

            timeout=3

        )


        print(

            "🧠 CONTEXT EVENT:",

            json.dumps(

                event,

                indent=2

            )

        )



    except Exception as e:


        print(

            "EVENT ERROR:",

            e

        )









# ======================================
# TEST LOOP
# ======================================


def start_analyzer():


    print(

        "🔥 JARVIS CONTEXT ANALYZER STARTED"

    )



    while True:


        # Temporary test input

        activity = {


            "message":

            "User is watching YouTube"


        }



        event = analyze_context(

            activity

        )



        if event:


            send_event(

                event

            )



        time.sleep(10)









if __name__ == "__main__":


    start_analyzer()