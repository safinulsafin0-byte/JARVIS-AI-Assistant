// ======================================
// JARVIS AI COMMAND SCHEMA v2
// BEAST MODE ABILITY REGISTRY
// FULL 3D + DRAW + PARTICLE + SYSTEM
// ======================================


const JARVIS_TOOLS = {


// ======================================
// WORKSPACE CONTROL
// ======================================

open_workspace:{

description:

"Open hologram workspace",

parameters:[

"particles",

"draw",

"models"

]

},





// ======================================
// PARTICLE ENGINE
// ======================================

create_particle:{

description:

"Create and control particle holograms",

parameters:[

"galaxy",

"sphere",

"wave",

"fire",

"smoke",

"energy",

"custom"

]

},





particle_control:{

description:

"Control particle simulation",

parameters:[

"explode",

"clear",

"move",

"follow",

"freeze"

]

},





// ======================================
// DRAW ENGINE
// ======================================

draw_shape:{

description:

"Create any hologram drawing",

parameters:[


"circle",

"square",

"triangle",

"cube",

"sphere",

"spiral",

"line",

"star",

"car",

"robot",

"house",

"custom"


]

},





// ======================================
// 3D MODEL ENGINE
// ======================================

load_model:{

description:

"Load and generate 3D hologram model",

parameters:[


"human",

"robot",

"car",

"vehicle",

"planet",

"earth",

"moon",

"building",

"house",

"cube",

"sphere",

"dna",

"dna hologram",

"double helix"


]

},





// ======================================
// TRANSFORMATION
// ======================================

transform:{

description:

"Transform 3D hologram objects",

parameters:[


"rotate",

"rotate_fast",

"scale_up",

"scale_down",

"move",

"reset"


]

},





// ======================================
// COLOR CONTROL
// ======================================

change_color:{

description:

"Change hologram color",

parameters:[


"cyan",

"blue",

"green",

"red",

"purple",

"white",

"yellow"


]

},





// ======================================
// HAND GESTURE
// ======================================

hand_control:{

description:

"Control hologram using hand gestures",

parameters:[


"enable",

"disable",

"follow",

"grab",

"release"


]

},





// ======================================
// SYSTEM CONTROL
// ======================================

system_control:{

description:

"Control JARVIS system",

parameters:[


"status",

"clear",

"reset",

"shutdown",

"restart"


]

},





// ======================================
// AI DRAWING AGENT
// ======================================

ai_draw:{

description:

"Generate drawing from natural language",

parameters:[


"any object",

"any shape",

"any design",

"futuristic object",

"architecture",

"vehicle",

"machine"


]

}





};






// ======================================
// MODEL ALIASES
// ======================================


const MODEL_ALIASES = {


"dna model":"dna",

"dna hologram":"dna",

"double helix":"dna",

"car model":"car",

"futuristic car":"car",

"vehicle":"car",

"robot model":"robot",

"robotic human":"robot",

"box":"cube",

"ball":"sphere",

"ring":"circle"


};






// ======================================
// NORMALIZER
// ======================================


function normalizeCommandModel(input){


input = String(input)
.toLowerCase()
.trim();



return MODEL_ALIASES[input] || input;


}







// ======================================
// EXPORT
// ======================================


window.JARVIS_TOOLS =

JARVIS_TOOLS;



window.MODEL_ALIASES =

MODEL_ALIASES;



window.normalizeCommandModel =

normalizeCommandModel;





console.log(

"🔥 JARVIS COMMAND SCHEMA v2 BEAST MODE LOADED"

);