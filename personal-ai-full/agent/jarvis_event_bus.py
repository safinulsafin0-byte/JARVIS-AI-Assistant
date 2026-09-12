# ======================================
# JARVIS EVENT BUS v1
# PROACTIVE AI EVENT SYSTEM
# ======================================


import requests



JARVIS_URL = "http://127.0.0.1:5002/event"




def send_jarvis_event(event):


    try:


        response = requests.post(

            JARVIS_URL,

            json=event,

            timeout=3

        )


        print(
            "EVENT SENT TO JARVIS:",
            response.json()
        )


    except Exception as e:


        print(
            "EVENT BUS ERROR:",
            e
        )