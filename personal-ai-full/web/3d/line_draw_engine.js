// ==========================================
// JARVIS 3D LINE DRAW ENGINE v2
// Hand Controlled Holographic Drawing
// ==========================================


let drawingActive = false;

let currentLine = null;

let currentPoints = [];

let drawnLines = [];





// ==========================================
// START DRAW MODE
// ==========================================


function startLineMode(){



    drawingActive = true;


    currentPoints=[];


    currentLine=null;



    updateLineStatus(
        "LINE DRAW MODE ACTIVE"
    );



    console.log(
        "JARVIS Line Drawing Enabled"
    );



}









// ==========================================
// STOP DRAW MODE
// ==========================================


function deactivateLineMode(){



    drawingActive=false;



    currentLine=null;


    currentPoints=[];



    updateLineStatus(
        "LINE MODE OFF"
    );



}









// ==========================================
// RECEIVE HAND POSITION
// ==========================================


function drawWithHand(
x,
y,
z=0
){



    if(!drawingActive)
        return;



    const point =

    new THREE.Vector3(


        (x-0.5)*8,


        -(y-0.5)*5,


        z*3


    );





    currentPoints.push(
        point
    );




    createOrUpdateLine();



}









// ==========================================
// CREATE / UPDATE LINE
// ==========================================


function createOrUpdateLine(){



    if(
        currentPoints.length < 2
    )

    return;






    const geometry =

    new THREE.BufferGeometry()
    .setFromPoints(
        currentPoints
    );







    const material =

    new THREE.LineBasicMaterial({

        color:0x00ffff,

        transparent:true,

        opacity:0.9

    });







    if(currentLine){



        if(
            typeof hologramScene !== "undefined"
        ){

            hologramScene.remove(
                currentLine
            );

        }


    }








    currentLine =

    new THREE.Line(

        geometry,

        material

    );







    currentLine.name =

    "JARVIS_DRAW_LINE";








    if(
        typeof hologramScene !== "undefined"
    ){



        hologramScene.add(
            currentLine
        );


    }






}









// ==========================================
// FINISH STROKE
// ==========================================


function finishStroke(){



    if(
        currentLine
    ){


        drawnLines.push(
            currentLine
        );


    }



    currentPoints=[];


    currentLine=null;



}









// ==========================================
// CLEAR
// ==========================================


function clearDrawings(){



    if(
        typeof hologramScene !== "undefined"
    ){



        drawnLines.forEach(

            line=>{


                hologramScene.remove(
                    line
                );


            }

        );


    }






    drawnLines=[];


    currentPoints=[];


    currentLine=null;



    updateLineStatus(
        "DRAWING CLEARED"
    );



}









// ==========================================
// UI
// ==========================================


function updateLineStatus(text){



    const ids=[

        "currentMode",

        "workspaceTitle",

        "modeText"

    ];




    ids.forEach(id=>{


        const el =
        document.getElementById(id);



        if(el){

            el.innerText=text;

        }



    });



}









// ==========================================
// EXPORT
// ==========================================


window.startLineMode =
startLineMode;



window.deactivateLineMode =
deactivateLineMode;



window.drawWithHand =
drawWithHand;



window.finishStroke =
finishStroke;



window.clearDrawings =
clearDrawings;