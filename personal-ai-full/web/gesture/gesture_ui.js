// ======================================
// JARVIS GESTURE UI CONTROLLER
// ======================================


let gestureEnabled = false;



window.addEventListener(
"load",
()=>{


const button =
document.getElementById(
"gestureButton"
);



if(!button){

console.error(
"Gesture button missing"
);

return;

}




button.addEventListener(
"click",
()=>{


    if(
        typeof JarvisHandTracker === "undefined"
    ){


        console.error(
        "Hand tracker not loaded"
        );


        return;


    }



    if(!gestureEnabled){


        JarvisHandTracker.start();


        gestureEnabled=true;


        button.innerText =
        "GESTURE ON";



    }

    else{


        JarvisHandTracker.stop();


        gestureEnabled=false;


        button.innerText =
        "GESTURE";



    }



});



console.log(
"Gesture UI Ready"
);



});