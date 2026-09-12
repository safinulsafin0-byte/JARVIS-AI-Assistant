// ======================================
// JARVIS 3D ENGINE v15
// BEAST MODE STABLE ENGINE
// DNA + ROBOT + CAR + CUBE + SPHERE + CIRCLE
// POPUP SAFE + AI COMMAND READY
// ======================================


let scene = null;
let camera = null;
let renderer = null;

let hologramObjects = [];

let threeReady = false;

let targetWindow = null;

let rotationSpeed = 0.03;

let animationStarted = false;



// ======================================
// INIT ENGINE
// ======================================


function init3DScene(){


if(threeReady){

console.log(
"3D ENGINE ALREADY ACTIVE"
);

return;

}



console.log(
"INITIALIZING 3D ENGINE"
);



targetWindow=null;



if(typeof getHologramWindow==="function"){


let win=getHologramWindow();


if(win && !win.closed){

targetWindow=win;

}

}



let win = targetWindow || window;



scene = new THREE.Scene();



camera = new THREE.PerspectiveCamera(

45,

win.innerWidth / win.innerHeight,

0.1,

1000

);



camera.position.set(
0,
0,
12
);





renderer = new THREE.WebGLRenderer({

alpha:true,

antialias:true,

powerPreference:"high-performance"

});



renderer.setPixelRatio(

win.devicePixelRatio || 1

);



renderer.setSize(

win.innerWidth,

win.innerHeight

);



renderer.setClearColor(
0x000000,
0
);





renderer.domElement.style.position="absolute";

renderer.domElement.style.top="0";

renderer.domElement.style.left="0";

renderer.domElement.style.width="100%";

renderer.domElement.style.height="100%";

renderer.domElement.style.zIndex="50";

renderer.domElement.style.pointerEvents="none";





if(targetWindow){

targetWindow.document.body.appendChild(
renderer.domElement
);

}

else{

document.body.appendChild(
renderer.domElement
);

}





win.addEventListener(
"resize",
resize3D
);



threeReady=true;



if(!animationStarted){

animationStarted=true;

animate3D();

}



console.log(
"3D ENGINE READY"
);


}







// ======================================
// RESIZE
// ======================================


function resize3D(){


if(!renderer || !camera)

return;



let win=targetWindow || window;



camera.aspect =
win.innerWidth /
win.innerHeight;



camera.updateProjectionMatrix();



renderer.setSize(

win.innerWidth,

win.innerHeight

);


}







// ======================================
// ANIMATION LOOP
// ======================================


function animate3D(){


requestAnimationFrame(
animate3D
);



hologramObjects.forEach(obj=>{


obj.rotation.y += rotationSpeed;


obj.rotation.x += rotationSpeed*0.5;


});



if(renderer && scene && camera){

renderer.render(
scene,
camera
);

}



}







// ======================================
// MATERIAL FIXED
// ======================================


function hologramMaterial(){


return new THREE.MeshBasicMaterial({


color:new THREE.Color(
0x00ffff
),


wireframe:true,


transparent:true,


opacity:0.85,


depthWrite:false


});


}







// ======================================
// CREATE OBJECT
// ======================================


function create3DObject(type){


if(!threeReady){

init3DScene();

}



type = String(type)
.toLowerCase()
.trim();



console.log(
"CREATE MODEL:",
type
);



let geometry;



switch(type){


case "cube":

geometry =
new THREE.BoxGeometry(
2,
2,
2
);

break;



case "sphere":

geometry =
new THREE.SphereGeometry(
1.5,
64,
64
);

break;



case "circle":

geometry =
new THREE.TorusGeometry(
1.5,
0.06,
32,
120
);

break;



case "robot":

geometry =
new THREE.BoxGeometry(
2,
3,
1
);

break;



case "car":

geometry =
new THREE.BoxGeometry(
4,
1,
2
);

break;



default:

geometry =
new THREE.BoxGeometry(
2,
2,
2
);


}




let mesh =
new THREE.Mesh(

geometry,

hologramMaterial()

);



mesh.position.set(
0,
0,
0
);

scene.add(mesh);

hologramObjects.push(mesh);

console.log(
"MODEL CREATED:",
type
);
}
// ======================================
// DNA HOLOGRAM
// ======================================


function createDNA(){


let group = new THREE.Group();



for(let i=0;i<360;i++){


let angle = i * 0.18;


let y = (i * 0.035)-6;


let r = 1.2;



let x1 = Math.cos(angle)*r;

let z1 = Math.sin(angle)*r;



let x2 = -Math.cos(angle)*r;

let z2 = -Math.sin(angle)*r;





let material = hologramMaterial();





let atom1 = new THREE.Mesh(

new THREE.SphereGeometry(

0.07,

16,

16

),

material

);





let atom2 = new THREE.Mesh(

new THREE.SphereGeometry(

0.07,

16,

16

),

material

);





atom1.position.set(

x1,

y,

z1

);



atom2.position.set(

x2,

y,

z2

);





group.add(atom1);

group.add(atom2);







let lineGeometry = new THREE.BufferGeometry();



lineGeometry.setFromPoints([


new THREE.Vector3(

x1,

y,

z1

),


new THREE.Vector3(

x2,

y,

z2

)


]);






let line = new THREE.Line(

lineGeometry,


new THREE.LineBasicMaterial({

color:0x00ffff,

transparent:true,

opacity:0.5

})

);



group.add(line);



}





group.scale.set(

0.8,

0.8,

0.8

);



scene.add(group);



hologramObjects.push(group);



console.log(
"DNA HOLOGRAM CREATED"
);



}









// ======================================
// CLEAR ALL OBJECTS
// ======================================


function clear3DObjects(){



if(!scene)

return;



hologramObjects.forEach(obj=>{


scene.remove(obj);



if(obj.geometry){

obj.geometry.dispose();

}



if(obj.material){


if(Array.isArray(obj.material)){


obj.material.forEach(m=>m.dispose());


}

else{


obj.material.dispose();


}


}



});




hologramObjects=[];



console.log(
"3D OBJECTS CLEARED"
);



}









// ======================================
// NORMALIZE COMMAND
// ======================================


function normalizeModelName(model){


model = String(model)
.toLowerCase()
.trim();



const map={


"dna":"dna",

"dna model":"dna",


"robot":"robot",

"robot model":"robot",


"car":"car",

"vehicle":"car",

"futuristic car":"car",


"cube":"cube",

"box":"cube",


"sphere":"sphere",

"ball":"sphere",


"circle":"circle",

"ring":"circle"



};



return map[model] || model;



}









// ======================================
// CREATE MODEL FROM AI COMMAND
// ======================================


function createModelFromCommand(model){



model = normalizeModelName(model);



console.log(

"NORMALIZED MODEL:",

model

);




if(!threeReady){

init3DScene();

}



clear3DObjects();





if(model==="dna"){


createDNA();


}

else{


create3DObject(model);


}



}









// ======================================
// AI MODEL LOADER
// ======================================


function loadAIModel(model){



console.log(

"AI LOAD MODEL:",

model

);





if(typeof openHologramWorkspace==="function"){


openHologramWorkspace(

"models"

);


}






setTimeout(()=>{


createModelFromCommand(model);



},500);



}









// ======================================
// ROTATION CONTROL
// ======================================


function setRotationSpeed(speed){


speed = Number(speed);



if(!isNaN(speed)){


rotationSpeed = speed;


}



}









// ======================================
// RESET ENGINE
// ======================================


function resetHologram(){



clear3DObjects();



if(renderer){


renderer.dispose();


}



scene=null;

camera=null;

renderer=null;



threeReady=false;

animationStarted=false;



console.log(

"JARVIS 3D RESET COMPLETE"

);



}
// ======================================
// DRAWING CONNECTOR
// ======================================


function drawShape(shape){


shape = normalizeModelName(shape);



console.log(

"DRAW SHAPE:",

shape

);



if(!threeReady){

init3DScene();

}



clear3DObjects();



if(shape==="circle"){


create3DObject(
"circle"
);


return;


}



create3DObject(shape);



}









// ======================================
// AI SHAPE GENERATOR
// ======================================


function generateShapeFromAI(command){



command = String(command)
.toLowerCase();



let shape="cube";



if(command.includes("circle")){

shape="circle";

}

else if(command.includes("sphere")){

shape="sphere";

}

else if(command.includes("ball")){

shape="sphere";

}

else if(command.includes("robot")){

shape="robot";

}

else if(command.includes("car")){

shape="car";

}

else if(command.includes("dna")){

shape="dna";

}

else if(command.includes("cube")){

shape="cube";

}



drawShape(shape);



}









// ======================================
// MODEL TRANSFORM
// ======================================


function rotate3D(){


hologramObjects.forEach(obj=>{


obj.rotation.y += 0.5;


});


}




function scale3DObject(value){


hologramObjects.forEach(obj=>{


obj.scale.multiplyScalar(
value
);


});


}









// ======================================
// COLOR CONTROL
// ======================================


function changeHologramColor(color){



let c;



try{


c=new THREE.Color(color);


}

catch(e){


c=new THREE.Color(
0x00ffff
);


}




hologramObjects.forEach(obj=>{


if(obj.material){


obj.material.color=c;


}



});



}









// ======================================
// COMMAND TEST FUNCTIONS
// ======================================


function testCube(){


openHologramWorkspace(
"models"
);



setTimeout(()=>{


loadAIModel(
"cube"
);


},500);



}



function testRobot(){


openHologramWorkspace(
"models"
);



setTimeout(()=>{


loadAIModel(
"robot"
);


},500);



}



function testCar(){


openHologramWorkspace(
"models"
);



setTimeout(()=>{


loadAIModel(
"car"
);


},500);



}



function testCircle(){


openHologramWorkspace(
"draw"
);



setTimeout(()=>{


drawShape(
"circle"
);


},500);



}









// ======================================
// EXPORT
// ======================================


window.init3DScene =
init3DScene;


window.create3DObject =
create3DObject;


window.createDNA =
createDNA;


window.loadAIModel =
loadAIModel;


window.clear3DObjects =
clear3DObjects;


window.drawShape =
drawShape;


window.generateShapeFromAI =
generateShapeFromAI;


window.rotate3D =
rotate3D;


window.scale3DObject =
scale3DObject;


window.changeHologramColor =
changeHologramColor;


window.resetHologram =
resetHologram;


window.testCube =
testCube;


window.testRobot =
testRobot;


window.testCar =
testCar;


window.testCircle =
testCircle;



console.log(

"🔥 JARVIS 3D ENGINE v15 PART 3 READY"

);
// ======================================
// JARVIS 3D ENGINE v15
// FINAL AI CONNECTION LAYER
// ======================================



// ======================================
// AI ART COMMAND SUPPORT
// ======================================


function createAIArt(prompt){


console.log(

"AI ART PROMPT:",

prompt

);



generateShapeFromAI(prompt);



}









// ======================================
// DRAWING AGENT CONNECTION
// ======================================


window.handleAIDrawing=function(prompt){



console.log(

"AI DRAWING REQUEST:",

prompt

);



openHologramWorkspace(
"draw"
);



setTimeout(()=>{


createAIArt(prompt);



},600);



};









// ======================================
// AI MODEL OVERRIDE
// ======================================


window.loadAIModel=function(model){



console.log(

"JARVIS MODEL REQUEST:",

model

);



if(typeof openHologramWorkspace==="function"){


openHologramWorkspace(
"models"
);


}



setTimeout(()=>{


createModelFromCommand(model);



},500);



};









// ======================================
// AI DRAW OVERRIDE
// ======================================


window.drawAIShape=function(shape){



console.log(

"JARVIS DRAW:",
shape

);



drawShape(shape);



};









// ======================================
// AI COMMAND TEST
// ======================================


window.jarvis3DTest=function(){



console.log(
"===== JARVIS 3D TEST ====="
);



loadAIModel(
"dna"
);



setTimeout(()=>{


loadAIModel(
"robot"
);


},3000);



setTimeout(()=>{


drawShape(
"circle"
);


},6000);



};









// ======================================
// GLOBAL EXPORT
// ======================================


window.setRotationSpeed =
setRotationSpeed;



window.rotate3D =
rotate3D;



window.scale3DObject =
scale3DObject;



window.changeHologramColor =
changeHologramColor;



window.generateShapeFromAI =
generateShapeFromAI;



window.createAIArt =
createAIArt;



window.handleAIDrawing =
handleAIDrawing;



console.log(

"🔥🔥 JARVIS 3D ENGINE v15 FINAL BEAST MODE READY 🔥🔥"

);