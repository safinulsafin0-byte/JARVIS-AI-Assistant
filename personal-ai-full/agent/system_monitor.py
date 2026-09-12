# ======================================
# JARVIS SYSTEM MONITOR AGENT v2
# CPU + RAM WATCHER ONLY
# ======================================


import psutil
import time
import requests
import json



EVENT_URL = "http://127.0.0.1:5002/event"



CPU_LIMIT = 90
RAM_LIMIT = 90



last_alert = ""





# ======================================
# GET SYSTEM STATUS
# ======================================


def get_system_status():


    cpu = psutil.cpu_percent(

        interval=1

    )


    ram = psutil.virtual_memory().percent



    return {


        "cpu": round(cpu,2),

        "ram": round(ram,2)

    }









# ======================================
# ALERT ENGINE
# ======================================


def analyze(status):


    global last_alert



    message = None



    if status["cpu"] > CPU_LIMIT:


        message = (

            "Warning. CPU usage is very high."

        )



    elif status["ram"] > RAM_LIMIT:


        message = (

            "Warning. Memory usage is very high."

        )





    if message and message != last_alert:


        last_alert = message


        return {


            "type":

            "system_alert",


            "message":

            message,


            "data":

            status

        }




    return None







# ======================================
# SEND EVENT
# ======================================


def send_event(event):


    try:


        response = requests.post(

            EVENT_URL,

            json=event,

            timeout=3

        )


        print(

            "🧠 JARVIS SYSTEM EVENT:",

            json.dumps(

                event,

                indent=2

            )

        )


    except Exception as e:


        print(

            "❌ EVENT ERROR:",

            e

        )









# ======================================
# MAIN LOOP
# ======================================


def start_monitor():


    print(

        "🔥 JARVIS CPU RAM MONITOR STARTED"

    )



    while True:


        status = get_system_status()



        print(

            "SYSTEM:",

            status

        )



        event = analyze(

            status

        )



        if event:


            send_event(

                event

            )



        time.sleep(10)









if __name__ == "__main__":


    start_monitor()