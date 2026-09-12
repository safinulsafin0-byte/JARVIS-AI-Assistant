// ======================================
// JARVIS HOLOGRAM ENGINE v16
// FINAL BEAST MODE STABLE FIX
// POPUP + PARTICLE + DRAW + 3D READY
// MODE SWITCH FIX
// MULTI COMMAND FIX
// ======================================


let holoCanvas = null;
let holoCtx = null;


let holoActive = false;

let currentMode = "";


let holoParticles = [];


let handX = 0.5;
let handY = 0.5;


let grabbed = false;


let animationID = null;


let hologramWindow = null;


let holoStarted = false;







// ======================================
// OPEN WORKSPACE
// ======================================


function openHologramWorkspace(type){


console.log(
"OPEN WORKSPACE:",
type
);





// IF WINDOW EXISTS → SWITCH MODE ONLY


if(
hologramWindow &&
!hologramWindow.closed
){


hologramWindow.focus();



currentMode = type;


holoActive = true;




if(type==="particles"){


startParticleEngine();


}



if(type==="draw"){


startDrawSpace();


}



if(type==="models"){


if(typeof init3DScene==="function"){


init3DScene();


}


}




console.log(

"MODE SWITCHED:",

currentMode

);



return;


}








// CREATE WINDOW


hologramWindow = window.open(

"",
"JARVIS_HOLOGRAM",

"width=1400,height=900"

);





if(!hologramWindow){


console.error(

"POPUP BLOCKED"

);


return;


}









hologramWindow.document.write(`


<!DOCTYPE html>

<html>

<head>

<title>JARVIS HOLOGRAM</title>


<style>


html,body{

margin:0;

padding:0;

width:100%;

height:100%;

overflow:hidden;

background:black;

}



#title{

position:absolute;

top:25px;

left:35px;

color:#00ffff;

font-size:30px;

font-family:Arial;

font-weight:bold;

z-index:100;

text-shadow:0 0 20px cyan;

}



canvas{

position:absolute;

top:0;

left:0;

}


</style>


</head>


<body>


<div id="title">

JARVIS ${type.toUpperCase()} SPACE

</div>


</body>

</html>


`);



hologramWindow.document.close();









// CANVAS CREATE


holoCanvas =
hologramWindow.document.createElement(
"canvas"
);



holoCanvas.id="holoCanvas";



hologramWindow.document.body.appendChild(

holoCanvas

);





holoCtx =
holoCanvas.getContext(
"2d"
);






resizeHoloCanvas();






hologramWindow.onresize =
resizeHoloCanvas;



hologramWindow.onbeforeunload=function(){


hologramWindow=null;

holoCanvas=null;

holoCtx=null;

holoActive=false;

currentMode="";


};








holoActive=true;

currentMode=type;








if(type==="particles"){


startParticleEngine();


}



if(type==="draw"){


startDrawSpace();


}



if(type==="models"){



setTimeout(()=>{


if(typeof init3DScene==="function"){


init3DScene();


}


},300);



}







if(!holoStarted){


holoStarted=true;

animateHologram();


}



}









// ======================================
// WINDOW ACCESS
// ======================================


function getHologramWindow(){


return hologramWindow;


}









// ======================================
// RESIZE
// ======================================


function resizeHoloCanvas(){


if(!holoCanvas)

return;




let w =
hologramWindow ?

hologramWindow.innerWidth :

window.innerWidth;



let h =
hologramWindow ?

hologramWindow.innerHeight :

window.innerHeight;






holoCanvas.width=w;

holoCanvas.height=h;



}









// ======================================
// PARTICLE ENGINE
// ======================================


function startParticleEngine(){



if(!holoCanvas)

return;



holoParticles=[];



for(let i=0;i<8000;i++){



holoParticles.push({


x:Math.random()*holoCanvas.width,


y:Math.random()*holoCanvas.height,


vx:(Math.random()-0.5)*2,


vy:(Math.random()-0.5)*2,


size:Math.random()*3+0.5



});



}



console.log(

"PARTICLES CREATED:",

holoParticles.length

);



}









// ======================================
// DRAW PARTICLES
// ======================================


function drawParticles(){



if(!holoCtx)

return;




holoParticles.forEach(p=>{


if(grabbed){



let tx =
handX*holoCanvas.width;


let ty =
handY*holoCanvas.height;




p.x +=
(tx-p.x)*0.03;



p.y +=
(ty-p.y)*0.03;



}

else{


p.x+=p.vx;

p.y+=p.vy;




if(
p.x<0 ||
p.x>holoCanvas.width
)

p.vx*=-1;




if(
p.y<0 ||
p.y>holoCanvas.height
)

p.vy*=-1;



}





holoCtx.fillStyle="#00ffff";


holoCtx.beginPath();


holoCtx.arc(

p.x,

p.y,

p.size,

0,

Math.PI*2

);



holoCtx.fill();



});



}









// ======================================
// LOOP
// ======================================


function animateHologram(){



if(!holoActive)

return;





if(holoCtx){



holoCtx.clearRect(

0,

0,

holoCanvas.width,

holoCanvas.height

);






if(currentMode==="particles"){


drawParticles();


}



}




animationID=requestAnimationFrame(

animateHologram

);



}









// ======================================
// HAND CONTROL
// ======================================


function updateHologramHand(x,y){


handX=x;

handY=y;


}



function hologramPinch(){


grabbed=true;


}



function hologramRelease(){


grabbed=false;


}









// ======================================
// CLEAR
// ======================================


function hologramClear(){



holoParticles=[];



if(typeof clear3DObjects==="function"){


clear3DObjects();


}



console.log(

"HOLOGRAM CLEARED"

);



}









// ======================================
// DRAW MODE
// ======================================


function startDrawSpace(){



console.log(

"DRAW SPACE ACTIVE"

);



}








function drawAIShape(shape){



console.log(

"DRAW COMMAND:",

shape

);



openHologramWorkspace(

"draw"

);



setTimeout(()=>{


if(typeof create3DObject==="function"){


create3DObject(

shape

);


}



},500);



}









// ======================================
// PARTICLE EFFECT
// ======================================


function hologramExplosion(){



holoParticles.forEach(p=>{


p.x +=
(Math.random()-0.5)*800;


p.y +=
(Math.random()-0.5)*800;



});



}









function moveParticles(dx,dy){



holoParticles.forEach(p=>{


p.x +=
dx*holoCanvas.width;


p.y +=
dy*holoCanvas.height;



});



}









// ======================================
// EXPORT
// ======================================


window.openHologramWorkspace =
openHologramWorkspace;



window.getHologramWindow =
getHologramWindow;



window.startParticleEngine =
startParticleEngine;



window.updateHologramHand =
updateHologramHand;



window.hologramPinch =
hologramPinch;



window.hologramRelease =
hologramRelease;



window.hologramClear =
hologramClear;



window.hologramExplosion =
hologramExplosion;



window.moveParticles =
moveParticles;



window.drawAIShape =
drawAIShape;





console.log(

"🔥 JARVIS HOLOGRAM ENGINE v16 FINAL BEAST READY"

);