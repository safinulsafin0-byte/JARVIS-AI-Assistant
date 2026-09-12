# ======================================
# JARVIS BROWSER MONITOR AGENT v1
# ACTIVE PAGE TRACKER
# ======================================


from flask import Flask, request, jsonify
from flask_cors import CORS
import time



app = Flask(__name__)


# Enable Chrome Extension access
CORS(app)



# Store current browser state

current = {

    "url": "",

    "title": "",

    "time": 0

}





# ======================================
# RECEIVE BROWSER DATA
# ======================================


@app.route(
    "/browser",
    methods=["POST"]
)

def browser():


    global current



    data = request.json



    if data:


        current = {


            "url": data.get(
                "url",
                ""
            ),


            "title": data.get(
                "title",
                ""
            ),


            "time": time.time()


        }



        print(
            "🔥 JARVIS PAGE:",
            current
        )



    return jsonify({

        "status":"received"

    })







# ======================================
# GET CURRENT PAGE
# ======================================


@app.route(
    "/browser/status",
    methods=["GET"]
)

def status():


    return jsonify(current)








# ======================================
# HEALTH CHECK
# ======================================


@app.route(
    "/",
    methods=["GET"]
)

def home():


    return jsonify({

        "JARVIS":
        "Browser Monitor Online",

        "status":
        "ready"

    })








# ======================================
# START SERVER
# ======================================


if __name__ == "__main__":


    print(
        "🔥 JARVIS BROWSER MONITOR STARTED"
    )


    app.run(

        host="127.0.0.1",

        port=5051,

        debug=False

    )