// ======================================
// JARVIS AI DRAWING AGENT v1
// ======================================


function handleAIDrawing(prompt){


console.log(

"DRAWING AI:",

prompt

);



openHologramWorkspace(
"draw"
);



setTimeout(()=>{


generateShape(prompt);


},500);



}



function generateShape(prompt){



let text=prompt.toLowerCase();


if(text.includes("dna")
||
text.includes("gene")){


create3DObject(
"dna"
);

return;

}

if(text.includes("circle")
||
text.includes("ring")){


create3DObject(
"circle"
);

return;

}


if(text.includes("cube")
||
text.includes("box")){


create3DObject(
"cube"
);

return;

}

if(text.includes("sphere")
||
text.includes("ball")){


create3DObject(
"sphere"
);

return;

}

if(text.includes("robot")){


create3DObject(
"robot"
);

return;

}

if(text.includes("car")
||
text.includes("vehicle")){


create3DObject(
"car"
);

return;

}

// fallback


createAIObject(prompt);



}

function createAIObject(prompt){


console.log(

"UNKNOWN OBJECT:",

prompt

);

// temporary AI placeholder

create3DObject(
"sphere"
);



}

window.handleAIDrawing =
handleAIDrawing;

console.log(
"🔥 DRAWING AGENT READY"
);