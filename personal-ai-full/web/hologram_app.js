// ==========================================
// JARVIS HOLOGRAM APP CONTROLLER v2
// Particle + Line Workspace
// ==========================================


let currentHologramMode = "none";




// ==========================================
// INITIALIZE
// ==========================================


window.addEventListener(
"load",
()=>{


    console.log(
        "JARVIS Hologram App Loaded"
    );


    setupHologramButtons();


    autoStartSavedMode();


    updateMode(
        "SYSTEM READY"
    );


});







// ==========================================
// AUTO LOAD MODE
// ==========================================


function autoStartSavedMode(){


    const mode =
    localStorage.getItem(
        "hologramMode"
    );


    if(mode==="particles"){


        activateParticleMode();


    }


    if(mode==="lines"){


        startLineMode();


    }


}









// ==========================================
// BUTTONS
// ==========================================


function setupHologramButtons(){


    const particleBtn =
    document.getElementById(
        "particleBtn"
    );


    const lineBtn =
    document.getElementById(
        "lineBtn"
    );


    const clearBtn =
    document.getElementById(
        "clearBtn"
    );


    const backBtn =
    document.getElementById(
        "backBtn"
    );





    if(particleBtn){

        particleBtn.onclick =
        ()=>{

            activateParticleMode();

        };

    }





    if(lineBtn){

        lineBtn.onclick =
        ()=>{

            startLineMode();

        };

    }






    if(clearBtn){

        clearBtn.onclick =
        ()=>{


            if(
                typeof clearHologram==="function"
            ){

                clearHologram();

            }



            if(
                typeof clearDrawings==="function"
            ){

                clearDrawings();

            }



        };


    }







    if(backBtn){


        backBtn.onclick =
        ()=>{


            window.location.href =
            "/web/index.html";


        };


    }


}









// ==========================================
// PARTICLE MODE
// ==========================================


function activateParticleMode(){


    currentHologramMode =
    "particles";



    localStorage.setItem(
        "hologramMode",
        "particles"
    );






    if(
        typeof createParticleSystem==="function"
    ){


        createParticleSystem();


    }




    updateMode(
        "PARTICLE MODE ACTIVE"
    );



}




window.activateParticleMode =
activateParticleMode;









// ==========================================
// LINE MODE
// ==========================================


function startLineMode(){


    currentHologramMode =
    "lines";



    localStorage.setItem(
        "hologramMode",
        "lines"
    );







    if(
        typeof initLineDrawing==="function"
    ){

        initLineDrawing();

    }







    updateMode(
        "LINE DRAW MODE ACTIVE"
    );



}




window.startLineMode =
startLineMode;









// ==========================================
// VOICE COMMAND
// ==========================================


function processHologramCommand(text){



    if(!text)
        return;



    let command =
    text.toLowerCase();




    if(
        command.includes("particle")
    ){


        activateParticleMode();

        return;

    }






    if(
        command.includes("line") ||
        command.includes("draw")
    ){


        startLineMode();

        return;


    }






    if(
        command.includes("clear")
    ){


        if(
            typeof clearHologram==="function"
        ){

            clearHologram();

        }



        if(
            typeof clearDrawings==="function"
        ){

            clearDrawings();

        }


    }


}



window.processHologramCommand =
processHologramCommand;









// ==========================================
// UI STATUS
// ==========================================


function updateMode(text){



    const elements=[

        "currentMode",

        "modeText",

        "workspaceTitle"

    ];



    elements.forEach(id=>{


        const el =
        document.getElementById(id);


        if(el){

            el.innerText=text;

        }


    });


}









// ==========================================
// GESTURE CONNECTION
// ==========================================


function hologramGestureHandler(data){



    if(
        !data ||
        !data.landmarks
    )

    return;



    const index =
    data.landmarks[8];





    if(
        currentHologramMode==="lines"
    ){



        if(
            typeof drawWithHand==="function"
        ){


            drawWithHand(

                index.x,

                index.y,

                index.z

            );


        }


    }







    if(
        currentHologramMode==="particles"
    ){



        if(
            typeof moveParticles==="function"
        ){


            moveParticles(

                index.x-0.5,

                index.y-0.5

            );


        }


    }



}





window.hologramGestureHandler =
hologramGestureHandler;