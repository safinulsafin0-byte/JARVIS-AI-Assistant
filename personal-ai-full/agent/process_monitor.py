# ======================================
# JARVIS PROCESS MONITOR AGENT v2
# APPLICATION RESOURCE WATCHER
# FALSE ALERT FIXED
# ======================================


import psutil
import time
import requests
import json



EVENT_URL = "http://127.0.0.1:5002/event"



CPU_LIMIT = 80

MEMORY_LIMIT = 3000   # MB



last_alert = ""





# ======================================
# GET RUNNING PROCESSES
# ======================================


def get_processes():


    processes = []



    for p in psutil.process_iter(

        [

            "pid",

            "name",

            "cpu_percent",

            "memory_info"

        ]

    ):



        try:


            info = p.info



            name = info["name"]



            # Ignore Windows idle/system processes

            if name in [

                "System Idle Process",

                "Idle",

                "System"

            ]:

                continue





            memory = 0



            if info["memory_info"]:


                memory = (

                    info["memory_info"].rss

                    /

                    (1024*1024)

                )





            processes.append({


                "pid":

                info["pid"],



                "name":

                name,



                "cpu":

                info["cpu_percent"],



                "memory":

                round(memory,2)

            })





        except:

            pass





    return processes









# ======================================
# ANALYZE PROCESSES
# ======================================


def analyze_processes(processes):


    global last_alert



    alert = None





    for p in processes:



        # High CPU detection


        if p["cpu"] > CPU_LIMIT:



            alert = (

                f"{p['name']} is using high CPU."

            )



            break





        # High memory detection


        if p["memory"] > MEMORY_LIMIT:



            alert = (

                f"{p['name']} is using high memory."

            )



            break





    if alert and alert != last_alert:



        last_alert = alert



        return {


            "type":

            "system_alert",



            "message":

            alert

        }





    return None









# ======================================
# SEND EVENT TO JARVIS
# ======================================


def send_event(event):


    try:



        response = requests.post(


            EVENT_URL,


            json=event,


            timeout=3


        )



        print(


            "🧠 PROCESS EVENT:",


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
# MAIN MONITOR LOOP
# ======================================


def start_monitor():



    print(


        "🔥 JARVIS PROCESS MONITOR v2 STARTED"


    )





    while True:



        processes = get_processes()



        event = analyze_processes(

            processes

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



    start_monitor()