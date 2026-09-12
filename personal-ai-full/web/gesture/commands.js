// ======================================
// JARVIS GESTURE COMMAND MAP v7
// ======================================


const JARVIS_GESTURE_COMMANDS = {


    pinch:{
        name:"Select Hologram Object",
        action:"select"
    },


    open_palm:{
        name:"Open Hologram Menu",
        action:"menu"
    },


    fist:{
        name:"Stop Action",
        action:"stop"
    },


    point:{
        name:"Drawing Mode",
        action:"draw"
    }


};






// ======================================
// EXECUTE GESTURE
// ======================================


function executeGestureCommand(gesture){


    const command =
    JARVIS_GESTURE_COMMANDS[gesture];



    if(!command)
        return;



    console.log(
        "Executing:",
        command.name
    );



    switch(command.action){


        case "select":
            gestureSelect();
        break;


        case "menu":
            gestureMenu();
        break;


        case "stop":
            gestureStop();
        break;


        case "draw":
            gestureDraw();
        break;


    }


}








// ======================================
// SELECT
// ======================================


function gestureSelect(){


    updateGestureActivity(
        "OBJECT SELECTED"
    );



    if(typeof selectParticleObject==="function"){

        selectParticleObject();

    }



    if(typeof selectHologramObject==="function"){

        selectHologramObject();

    }


}








// ======================================
// MENU OPEN
// ======================================


function gestureMenu(){


    updateGestureActivity(
        "HOLOGRAM MENU OPEN"
    );


    openJarvisMenu();


}







function openJarvisMenu(){


    const menu =
    document.getElementById(
        "hologramMenu"
    );



    if(!menu){

        console.error(
            "hologramMenu missing"
        );

        return;

    }



    menu.classList.add(
        "active"
    );


    console.log(
        "JARVIS Menu Open"
    );


}







function closeJarvisMenu(){


    const menu =
    document.getElementById(
        "hologramMenu"
    );



    if(menu){

        menu.classList.remove(
            "active"
        );

    }


}








// ======================================
// STOP
// ======================================


function gestureStop(){


    updateGestureActivity(
        "ACTION STOPPED"
    );



    if(typeof clearDrawings==="function"){

        clearDrawings();

    }


}








// ======================================
// DRAW GESTURE
// ======================================


function gestureDraw(){


    localStorage.setItem(
        "hologramMode",
        "lines"
    );



    updateGestureActivity(
        "DRAW MODE ACTIVE"
    );



    if(typeof openHologramWorkspace==="function"){

        openHologramWorkspace(
            "draw"
        );

    }


}








// ======================================
// ACTIVITY
// ======================================


function updateGestureActivity(text){


    const activity =
    document.getElementById(
        "activityText"
    );


    if(activity){

        activity.innerText=text;

    }


}








// ======================================
// MENU BUTTONS
// ======================================


window.addEventListener(
"load",
()=>{



const particle =
document.getElementById(
"particleModeBtn"
);



const draw =
document.getElementById(
"drawModeBtn"
);



const models =
document.getElementById(
"modelModeBtn"
);



const files =
document.getElementById(
"fileModeBtn"
);



const voice =
document.getElementById(
"voiceModeBtn"
);



const system =
document.getElementById(
"systemModeBtn"
);



const close =
document.getElementById(
"closeMenuBtn"
);







// PARTICLE

if(particle){


particle.onclick=()=>{

localStorage.setItem(
"workspace",
"particles"
);

openHologramWorkspace("particles");


updateGestureActivity(
"PARTICLE ENGINE ACTIVE"
);


console.log(
"Particle system selected"
);

if(typeof createParticleSystem==="function"){

    createParticleSystem();

}


if(typeof openHologramWorkspace==="function"){

    openHologramWorkspace("particles");

}
if(typeof openHologramWorkspace === "function"){

    openHologramWorkspace(
        "particles"
    );

}
else{

    console.error(
        "openHologramWorkspace missing"
    );

}


};


}

// DRAW

if(draw){


draw.onclick=()=>{

if(
typeof createDrawSpace==="function"
){

createDrawSpace();

}
localStorage.setItem(
"workspace",
"draw"
);

openHologramWorkspace("draw");



updateGestureActivity(
"DRAW SPACE ACTIVE"
);



console.log(
"Draw system selected"
);



if(typeof openHologramWorkspace==="function"){

openHologramWorkspace(
"draw"
);

}



};


}

// MODELS

if(models){


openHologramWorkspace("models");


}


// FILE

if(files){


files.onclick=()=>{


updateGestureActivity(
"FILE SYSTEM"
);



console.log(
"File system selected"
);



if(typeof openHologramWorkspace==="function"){

openHologramWorkspace(
"files"
);

}



};


}

// VOICE

if(voice){


voice.onclick=()=>{


updateGestureActivity(
"VOICE CONTROL"
);



console.log(
"Voice control selected"
);



if(typeof openHologramWorkspace==="function"){

openHologramWorkspace(
"voice"
);

}



};


}

// SYSTEM

if(system){


system.onclick=()=>{


updateGestureActivity(
"SYSTEM STATUS"
);



if(typeof openHologramWorkspace==="function"){

openHologramWorkspace(
"system"
);

}



};


}
// CLOSE

if(close){


close.onclick=()=>{


closeJarvisMenu();


};


}



});


// ======================================
// EXPORT
// ======================================


window.executeGestureCommand =
executeGestureCommand;


window.openJarvisMenu =
openJarvisMenu;


window.closeJarvisMenu =
closeJarvisMenu;


window.gestureSelect =
gestureSelect;


window.gestureMenu =
gestureMenu;


window.gestureStop =
gestureStop;


window.gestureDraw =
gestureDraw;



console.log(
"JARVIS Gesture Commands v7 Loaded"
);