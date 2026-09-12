from flask import Flask,jsonify
import psutil
import GPUtil


app=Flask(__name__)


@app.route("/status")
def status():

    cpu=psutil.cpu_percent()

    ram=psutil.virtual_memory().percent


    gpu_data=[]

    try:

        gpus=GPUtil.getGPUs()

        for gpu in gpus:

            gpu_data.append({

                "name":gpu.name,

                "load":gpu.load*100,

                "memory":gpu.memoryUsed

            })


    except:

        pass



    battery=None

    try:

        battery=psutil.sensors_battery().percent

    except:

        pass



    return jsonify({

        "cpu":cpu,

        "ram":ram,

        "gpu":gpu_data,

        "battery":battery

    })



app.run(
host="127.0.0.1",
port=5050
)