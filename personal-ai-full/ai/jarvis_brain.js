// ======================================
// JARVIS BRAIN v4
// LLM COMMAND INTERPRETER
// BEAST MODE
// ======================================



async function jarvisThink(command){


console.log(
"USER:",
command
);



let action =
interpretCommand(command);



console.log(
"AI ACTION:",
action
);



if(
typeof executeAIAction==="function"
){

await executeAIAction(
action
);


}

else{


console.error(
"ACTION ROUTER NOT FOUND"
);


}



}



// ======================================
// COMMAND INTERPRETER
// ======================================


function interpretCommand(text){



text =
text.toLowerCase();





// ===============================
// OPEN PARTICLE
// ===============================


if(

text.includes("particle")
&&
(
text.includes("open")
||
text.includes("start")
||
text.includes("show")
||
text.includes("workspace")
)

){


return {


intent:
"open_workspace",


workspace:
"particles"


};


}





// ===============================
// OPEN DRAW SPACE
// ===============================


if(

text.includes("draw")
&&

(
text.includes("space")
||
text.includes("workspace")
||
text.includes("mode")
)

){


return {


intent:
"open_workspace",


workspace:
"draw"


};


}






// ===============================
// DRAW SHAPES
// ===============================


if(

text.includes("draw")

){



let shape="unknown";



if(
text.includes("circle")
)
shape="circle";



else if(
text.includes("square")
)
shape="square";



else if(
text.includes("cube")
)
shape="cube";



else if(
text.includes("sphere")
)
shape="sphere";



else if(
text.includes("triangle")
)
shape="triangle";




return {


intent:
"draw_shape",


shape:
shape


};



}






// ===============================
// CREATE OBJECT
// ===============================



if(

text.includes("create")
||
text.includes("make")
||
text.includes("generate")
||
text.includes("build")

){



let object="unknown";




if(
text.includes("dna")
)

object="dna";



else if(
text.includes("heart")
)

object="heart";



else if(
text.includes("robot")
)

object="robot";



else if(
text.includes("car")
)

object="car";



else if(
text.includes("human")
)

object="human";



else if(
text.includes("cube")
)

object="cube";



else if(
text.includes("sphere")
)

object="sphere";




return {


intent:
"load_model",


model:
object


};


}







// ===============================
// PARTICLE CONTROL
// ===============================



if(

text.includes("explode")
||
text.includes("burst")
||
text.includes("scatter")

){


return {


intent:
"particle_control",


command:
"explode"


};


}





// ===============================
// CLEAR
// ===============================


if(

text.includes("clear")
||
text.includes("delete")
||
text.includes("remove")
||
text.includes("reset")

){



return {


intent:
"system_control",


command:
"clear"


};


}






// ===============================
// COLORS
// ===============================


if(

text.includes("blue")
||
text.includes("red")
||
text.includes("green")
||
text.includes("cyan")

){



let color="blue";



if(text.includes("red"))
color="red";


if(text.includes("green"))
color="green";


if(text.includes("cyan"))
color="cyan";



return {


intent:
"change_color",


color:
color


};


}








// ===============================
// MOVEMENT
// ===============================



if(

text.includes("rotate")

){


return {


intent:
"transform",


action:
"rotate"


};


}





if(

text.includes("bigger")
||
text.includes("increase")
||
text.includes("scale")

){


return {


intent:
"transform",


action:
"scale_up"


};


}





if(

text.includes("smaller")
||
text.includes("reduce")

){


return {


intent:
"transform",


action:
"scale_down"


};


}







// ===============================
// UNKNOWN
// ===============================


return {


intent:
"unknown",


text:
command


};



}






// ======================================
// EXPORT
// ======================================


window.jarvisThink =
jarvisThink;


window.interpretCommand =
interpretCommand;



console.log(
"JARVIS BRAIN v4 LOADED"
);