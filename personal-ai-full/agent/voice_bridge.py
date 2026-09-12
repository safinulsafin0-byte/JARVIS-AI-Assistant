# ======================================
# JARVIS VOICE BRIDGE
# ======================================

from flask import Flask,request,jsonify

import queue


app = Flask(__name__)


voice_queue = queue.Queue()



@app.route(
"/speak",
methods=["POST"]
)

def speak():


    data=request.json


    message=data.get(
        "message",
        ""
    )


    if message:


        voice_queue.put(
            message
        )


        print(
            "🔊 VOICE REQUEST:",
            message
        )


    return jsonify({

        "status":"queued"

    })





@app.route(
"/voice/get"
)

def get_voice():


    if not voice_queue.empty():

        return jsonify({

            "message":
            voice_queue.get()

        })


    return jsonify({

        "message":""

    })





if __name__=="__main__":


    print(
        "🔥 VOICE BRIDGE ONLINE"
    )


    app.run(

        host="127.0.0.1",

        port=5003

    )