// ======================================
// JARVIS AI ACTION ROUTER v3
// BEAST MODE AI COMMAND CONNECTOR
// ======================================



async function executeAIAction(action){


console.log(
"AI ACTION RECEIVED:",
action
);



if(!action)
return;




switch(action.intent){



// ======================================
// OPEN WORKSPACE
// ======================================


case "open_workspace":



console.log(
"OPEN WORKSPACE:",
action.workspace
);



if(
typeof openHologramWorkspace==="function"
){


openHologramWorkspace(

action.workspace

);


}


break;







// ======================================
// DRAW SHAPE
// ======================================


case "draw_shape":



console.log(
"DRAW SHAPE:",
action.shape
);



if(
typeof drawAIShape==="function"
){


drawAIShape(

action.shape

);


}

else{


console.warn(
"drawAIShape missing"
);


}



break;








// ======================================
// LOAD 3D MODEL
// ======================================


case "load_model":



console.log(
"LOAD MODEL:",
action.model
);



if(
typeof loadAIModel==="function"
){


loadAIModel(

action.model

);


}



else if(

typeof create3DObject==="function"

){


create3DObject(

action.model.toLowerCase()

);


}



else{


console.warn(
"3D MODEL ENGINE NOT CONNECTED"
);


}




break;








// ======================================
// PARTICLE CREATE
// ======================================


case "create_particle":



console.log(
"CREATE PARTICLE:",
action.type
);



if(

typeof createAIParticle==="function"

){


createAIParticle(

action.type

);


}



break;







// ======================================
// PARTICLE CONTROL
// ======================================


case "particle_control":



console.log(
"PARTICLE COMMAND:",
action.command
);



if(
action.command==="explode"
){


if(
typeof hologramExplosion==="function"
){


hologramExplosion();


}


}




if(
action.command==="hand_follow"
){


if(
typeof enableParticleFollow==="function"
){


enableParticleFollow();


}


}




break;









// ======================================
// COLOR CHANGE
// ======================================


case "change_color":



console.log(
"CHANGE COLOR:",
action.color
);



if(

typeof changeHologramColor==="function"

){


changeHologramColor(

action.color

);


}



break;









// ======================================
// TRANSFORM
// ======================================


case "transform":



console.log(
"TRANSFORM:",
action.action
);



if(

typeof transformHologram==="function"

){


transformHologram(

action.action

);


}



break;









// ======================================
// SYSTEM CONTROL
// ======================================


case "system_control":



if(

action.command==="clear"

){



if(

typeof hologramClear==="function"

){


hologramClear();


}



if(

typeof clear3DObjects==="function"

){


clear3DObjects();


}



}



break;









// ======================================
// UNKNOWN
// ======================================


case "unknown":



console.log(

"UNKNOWN COMMAND:",

action.text

);



break;







default:



console.log(

"UNSUPPORTED AI ACTION:",

action.intent

);



}




}




// ======================================
// EXPORT
// ======================================


window.executeAIAction =
executeAIAction;



console.log(

"JARVIS ACTION ROUTER v3 LOADED"

);