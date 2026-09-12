// ======================================
// JARVIS HAND TRACKER v5
// MediaPipe + Hologram Control
// ======================================


let jarvisHands = null;

let jarvisVideo = null;

let jarvisStream = null;


let handTrackingActive = false;

let latestHandData = null;

let trackerInitialized = false;


let processingFrame = false;





// ======================================
// INIT MEDIAPIPE
// ======================================


function initHandTracker(){



    if(trackerInitialized)

        return;





    jarvisVideo =

    document.getElementById(

        "gestureCamera"

    );





    if(!jarvisVideo){


        console.error(

            "JARVIS: gestureCamera missing"

        );


        return;


    }







    if(typeof Hands === "undefined"){



        console.error(

            "JARVIS: MediaPipe Hands missing"

        );


        return;


    }









    jarvisHands =

    new Hands({



        locateFile:(file)=>{


            return (

                "https://cdn.jsdelivr.net/npm/" +

                "@mediapipe/hands/" +

                file

            );


        }


    });









    jarvisHands.setOptions({



        maxNumHands:1,


        modelComplexity:1,


        minDetectionConfidence:0.7,


        minTrackingConfidence:0.7



    });







    jarvisHands.onResults(

        onHandResults

    );








    trackerInitialized=true;



    console.log(

        "JARVIS Hand Tracker Initialized"

    );



}











// ======================================
// START CAMERA
// ======================================


async function startHandTracking(){



    if(handTrackingActive)

        return;





    if(!trackerInitialized){

        initHandTracker();

    }





    if(!jarvisHands)

        return;







    try{



        jarvisStream =

        await navigator.mediaDevices

        .getUserMedia({



            video:{



                width:640,


                height:480,


                facingMode:"user"



            },


            audio:false



        });








        jarvisVideo.srcObject =

        jarvisStream;








        await jarvisVideo.play();







        handTrackingActive=true;





        updateGestureStatus(

            "HAND TRACKING ACTIVE"

        );







        processHandFrame();





        console.log(

            "JARVIS Gesture Camera Started"

        );



    }



    catch(error){



        console.error(

            "Camera Error:",

            error

        );



        updateGestureStatus(

            "CAMERA ERROR"

        );



    }



}












// ======================================
// FRAME LOOP
// ======================================


async function processHandFrame(){



    if(!handTrackingActive)

        return;








    if(

        !processingFrame &&

        jarvisVideo.readyState >= 2

    ){



        processingFrame=true;





        try{


            await jarvisHands.send({


                image:

                jarvisVideo


            });


        }


        catch(error){



            console.warn(

                "Frame Error:",

                error

            );


        }



        processingFrame=false;


    }







    requestAnimationFrame(

        processHandFrame

    );


}











// ======================================
// MEDIAPIPE RESULTS
// ======================================


function onHandResults(results){



    if(

        !results.multiHandLandmarks ||

        results.multiHandLandmarks.length===0

    ){



        latestHandData=null;



        updateGestureStatus(

            "HAND NOT FOUND"

        );



        return;


    }







    const landmarks =

    results.multiHandLandmarks[0];









    latestHandData={



        landmarks:landmarks,



        timestamp:Date.now(),




        handedness:


        results.multiHandedness?.[0]?.label

        ||

        "Unknown",





        wrist:

        landmarks[0],





        thumb:

        landmarks[4],





        index:

        landmarks[8],





        middle:

        landmarks[12],





        ring:

        landmarks[16],





        pinky:

        landmarks[20]



    };










    // gesture engine


    if(

        typeof processJarvisGesture ===

        "function"

    ){



        processJarvisGesture(

            latestHandData

        );


    }









    // hologram direct control


    if(

        typeof hologramGestureHandler ===

        "function"

    ){



        hologramGestureHandler(

            latestHandData

        );


    }




}












// ======================================
// STOP
// ======================================


function stopHandTracking(){



    handTrackingActive=false;







    if(jarvisStream){



        jarvisStream

        .getTracks()

        .forEach(

            track=>track.stop()

        );





        jarvisStream=null;



    }









    if(jarvisVideo){


        jarvisVideo.srcObject=null;


    }







    latestHandData=null;





    updateGestureStatus(

        "GESTURE OFF"

    );



}











// ======================================
// TOGGLE
// ======================================


function toggleHandTracking(){



    if(handTrackingActive){


        stopHandTracking();


    }

    else{


        startHandTracking();


    }



}











// ======================================
// STATUS
// ======================================


function updateGestureStatus(text){



    const el =

    document.getElementById(

        "gestureStatus"

    );




    if(el){


        el.innerText=text;


    }


}











// ======================================
// DATA
// ======================================


function getCurrentHand(){


    return latestHandData;


}











// ======================================
// GLOBAL API
// ======================================


window.JarvisHandTracker={



    start:

    startHandTracking,



    stop:

    stopHandTracking,



    toggle:

    toggleHandTracking,



    getData:

    getCurrentHand,



    active:

    ()=>handTrackingActive



};









// ======================================
// AUTO START
// ======================================


window.addEventListener(

"load",

()=>{



    console.log(

        "Starting JARVIS Hologram Gesture System"

    );





    initHandTracker();






    setTimeout(()=>{



        startHandTracking();



    },1000);



});








console.log(

"JARVIS Hand Tracker v5 Loaded"

);