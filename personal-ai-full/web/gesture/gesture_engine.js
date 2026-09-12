// ======================================
// JARVIS GESTURE ENGINE v12
// AI + HOLOGRAM BEAST MODE
// ======================================


let currentGesture="none";


let previousX=null;
let previousY=null;


let handTracked=false;


let lastGestureTime=0;


const gestureCooldown=1200;


const maxDelta=0.05;



// ======================================
// MAIN
// ======================================


function processJarvisGesture(handData){



// AI MODE BLOCK

if(
localStorage.getItem("jarvisMode")==="ai"
){

return;

}



if(
!handData ||
!handData.landmarks
){


handTracked=false;

previousX=null;
previousY=null;

return;


}



const points=
handData.landmarks;



controlHologramWithHand(points);



let gesture=
detectGesture(points);



let now=
Date.now();




if(

gesture!=="none"

&&

gesture!==currentGesture

&&

now-lastGestureTime>gestureCooldown

){



currentGesture=
gesture;


lastGestureTime=
now;



handleGesture(
gesture
);



}






trackHandMovement(points);


trackDrawing(points);





}







// ======================================
// HAND POSITION
// ======================================


function controlHologramWithHand(points){


let palm=
points[9];


if(!palm)
return;



if(
typeof updateHologramHand==="function"
){


updateHologramHand(
palm.x,
palm.y
);



}



}







// ======================================
// DETECTOR
// ======================================



function detectGesture(points){



let thumb=points[4];

let index=points[8];

let middle=points[12];

let ring=points[16];

let pinky=points[20];




// fingers


let indexOpen=
index.y < points[6].y;


let middleOpen=
middle.y < points[10].y;


let ringOpen=
ring.y < points[14].y;


let pinkyOpen=
pinky.y < points[18].y;



let count=[
indexOpen,
middleOpen,
ringOpen,
pinkyOpen
]
.filter(Boolean)
.length;





// FIST FIRST

if(count===0){

return "fist";

}






// PINCH


let pinchDistance=
distance(
thumb,
index
);



if(
pinchDistance<0.04
){

return "pinch";

}







// OPEN PALM


if(count===4){

return "open_palm";

}






// POINT


if(

indexOpen
&&
!middleOpen
&&
!ringOpen
&&
!pinkyOpen

){

return "point";

}



return "none";



}









// ======================================
// HANDLE
// ======================================


function handleGesture(g){



console.log(
"ACTIVE GESTURE:",
g
);



updateActivity(
g.toUpperCase()
);





switch(g){



case "pinch":


if(
typeof hologramPinch==="function"
){

hologramPinch();

}


break;







case "fist":



if(
typeof hologramRelease==="function"
){

hologramRelease();

}


break;









case "open_palm":



// ONLY PARTICLE

if(

localStorage.getItem("workspace")
==="particles"

){

if(
typeof hologramExplosion==="function"
){

hologramExplosion();

}


}



break;








case "point":



if(

localStorage.getItem("workspace")
==="draw"

){

console.log(
"DRAW ACTIVE"
);


}


break;




}




}









// ======================================
// MOVEMENT
// ======================================



function trackHandMovement(points){



let palm=
points[9];


if(!palm)
return;




if(
previousX===null ||
!handTracked
){


previousX=palm.x;

previousY=palm.y;


handTracked=true;


return;


}





let dx=
palm.x-previousX;


let dy=
palm.y-previousY;





// anti jump


dx=Math.max(
Math.min(dx,maxDelta),
-maxDelta
);


dy=Math.max(
Math.min(dy,maxDelta),
-maxDelta
);





previousX=palm.x;

previousY=palm.y;






if(

Math.abs(dx)>0.005

||

Math.abs(dy)>0.005

){





if(

localStorage.getItem("workspace")
==="particles"

&&

currentGesture==="pinch"

){



if(
typeof moveParticles==="function"
){

moveParticles(
dx,
dy
);


}


}







if(
typeof rotateHologram==="function"
){


rotateHologram(
dy*5,
dx*5
);



}





}





}












// ======================================
// DRAW
// ======================================



function trackDrawing(points){



let index=
points[8];



if(!index)
return;





if(

localStorage.getItem("workspace")
==="draw"

&&

currentGesture==="point"

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


else{


if(
typeof finishStroke==="function"
){

finishStroke();

}


}



}









// ======================================
// DISTANCE
// ======================================


function distance(a,b){


return Math.sqrt(

(a.x-b.x)**2

+

(a.y-b.y)**2

+

(a.z-b.z)**2


);


}









// ======================================
// UI
// ======================================


function updateActivity(t){



let el=
document.getElementById(
"activityText"
);



if(el)

el.innerText=t;



}









// ======================================
// RESET
// ======================================


function resetGesture(){


currentGesture="none";


}





window.processJarvisGesture=
processJarvisGesture;


window.detectGesture=
detectGesture;


window.resetGesture=
resetGesture;



console.log(
"JARVIS GESTURE ENGINE v12 AI STABLE LOADED"
);