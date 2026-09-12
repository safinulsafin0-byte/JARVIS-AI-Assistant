# ======================================
# JARVIS ACTIVITY WATCHER AGENT v3
# PROACTIVE USER ACTIVITY DETECTOR
# EVENT BUS CONNECTED
# ======================================


import requests
import time
import json



BROWSER_STATUS_URL = (
    "http://127.0.0.1:5051/browser/status"
)


JARVIS_EVENT_URL = (
    "http://127.0.0.1:5002/event"
)



last_activity = ""





# ======================================
# GET CURRENT PAGE
# ======================================


def get_browser_status():

    try:

        response = requests.get(
            BROWSER_STATUS_URL,
            timeout=3
        )

        return response.json()


    except Exception as e:

        print(
            "❌ Browser monitor error:",
            e
        )

        return None







# ======================================
# ACTIVITY ANALYZER
# ======================================


def analyze_activity(page):


    global last_activity



    if not page:

        return None



    title = page.get(
        "title",
        ""
    ).lower()



    url = page.get(
        "url",
        ""
    ).lower()





    if not title and not url:

        return None





    activity = None




    if "youtube" in title or "youtube" in url:


        activity = {

            "type":"entertainment",

            "message":
            "User is watching YouTube"

        }




    elif "google scholar" in title or "scholar.google" in url:


        activity = {

            "type":"research",

            "message":
            "User is doing research on Google Scholar"

        }




    elif "github" in url:


        activity = {

            "type":"coding",

            "message":
            "User is coding on GitHub"

        }




    elif "chatgpt" in url:


        activity = {

            "type":"ai_usage",

            "message":
            "User is using ChatGPT"

        }




    else:


        activity = {

            "type":"browsing",

            "message":
            "User is browsing " + page.get(
                "title",
                "unknown"
            )

        }






    if activity["message"] != last_activity:


        last_activity = activity["message"]

        return activity



    return None







# ======================================
# SEND EVENT TO JARVIS
# ======================================


def send_event(event):


    if not event:

        return



    print(

        "🔥 JARVIS EVENT:",

        json.dumps(
            event,
            indent=2
        )

    )



    try:


        response = requests.post(

            JARVIS_EVENT_URL,

            json=event,

            timeout=3

        )


        print(

            "🧠 EVENT SENT:",

            response.json()

        )


    except Exception as e:


        print(

            "❌ EVENT BUS ERROR:",

            e

        )








# ======================================
# MAIN LOOP
# ======================================


def start_watcher():


    print(
        "🔥 JARVIS ACTIVITY WATCHER v3 STARTED"
    )


    while True:


        page = get_browser_status()



        event = analyze_activity(
            page
        )



        if event:


            send_event(
                event
            )



        time.sleep(10)







# ======================================
# START
# ======================================


if __name__ == "__main__":


    start_watcher()