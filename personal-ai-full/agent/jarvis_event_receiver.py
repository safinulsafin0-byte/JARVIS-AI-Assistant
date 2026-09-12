# ======================================
# JARVIS EVENT RECEIVER v8
# PROACTIVE RESPONSE ENGINE
# TTS + CONTEXT MEMORY + WINDOW AWARENESS
# ======================================


from flask import Flask, request, jsonify
import requests
import threading



# ======================================
# CONTEXT MEMORY
# ======================================

from agent.context_memory import (
    update_context,
    should_speak,
    get_context_duration
)





app = Flask(__name__)





# ======================================
# SEND VOICE REQUEST
# ======================================


def send_voice(message):

    try:

        response = requests.post(

            "http://127.0.0.1:8000/api/speak",

            json={
                "text": message
            },

            timeout=10

        )


        print(

            "🔊 JARVIS TTS SENT:",

            response.json()

        )


    except Exception as e:


        print(

            "❌ TTS ERROR:",

            e

        )









# ======================================
# RECEIVE EVENT
# ======================================


@app.route(

    "/event",

    methods=["POST"]

)

def event():


    data = request.json



    print(

        "\n🧠 JARVIS EVENT RECEIVED:",

        data

    )



    response = process_event(

        data

    )



    print(

        "🤖 JARVIS RESPONSE:",

        response

    )



    # Non blocking voice

    if response:


        threading.Thread(

            target=send_voice,

            args=(response,),

            daemon=True

        ).start()



    return jsonify({


        "status":

        "processed",



        "response":

        response


    })









# ======================================
# AI DECISION ENGINE
# ======================================


def process_event(event):


    event_type = event.get(

        "type",

        ""

    )





    # ==================================
    # BROWSER ACTIVITY
    # ==================================


    if event_type == "entertainment":


        return (

            "You are watching YouTube. "

            "Stay focused on your task."

        )





    elif event_type == "research":


        return (

            "Research activity detected. "

            "Keep going."

        )





    elif event_type == "coding":


        return (

            "Coding activity detected."

        )





    elif event_type == "ai_usage":


        return (

            "You are using an AI assistant."

        )





    elif event_type == "browsing":


        return (

            "You are browsing the web."

        )









    # ==================================
    # SYSTEM MONITOR
    # ==================================


    elif event_type == "system_alert":


        return event.get(

            "message",

            "System alert detected."

        )









    # ==================================
    # CONTEXT ANALYZER
    # ==================================


    elif event_type == "context_change":


        return event.get(

            "message",

            "Context changed."

        )









    # ==================================
    # ACTIVE WINDOW MONITOR
    # ==================================


    elif event_type == "active_window":



        context = event.get(

            "context",

            "general"

        )


        application = event.get(

            "application",

            "unknown"

        )


        title = event.get(

            "title",

            ""

        )



        changed = update_context(

            context,

            application,

            title

        )



        # cooldown

        if not should_speak(

            context,

            cooldown=60

        ):

            return None



        duration = get_context_duration()



        if context == "coding":


            return (

                "Coding environment detected."

            )





        elif context == "browser":


            return (

                "Browser activity detected."

            )





        elif context == "document":


            return (

                "You are working on a document."

            )





        elif context == "reading":


            return (

                "You are reading a document."

            )





        elif context == "terminal":


            return (

                "Terminal activity detected."

            )





        else:


            return (

                f"Active application changed to {application}."

            )









    # ==================================
    # DEFAULT
    # ==================================


    else:


        return (

            "I detected your activity."

        )









# ======================================
# SERVER START
# ======================================


if __name__ == "__main__":


    print(

        "🔥 JARVIS EVENT RECEIVER v8 ONLINE"

    )


    app.run(

        host="127.0.0.1",

        port=5002

    )