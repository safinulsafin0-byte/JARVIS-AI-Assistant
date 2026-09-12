// ======================================
// JARVIS VOICE ENGINE v1
// SPEECH TO COMMAND
// ======================================


let recognition;


function initJarvisVoice(){


console.log(
"VOICE SYSTEM INITIALIZING"
);



const SpeechRecognition =
window.SpeechRecognition ||
window.webkitSpeechRecognition;



if(!SpeechRecognition){

console.error(
"Speech Recognition not supported"
);

return;

}



recognition =
new SpeechRecognition();



recognition.continuous=false;

recognition.interimResults=false;

recognition.lang="en-US";





recognition.onstart=()=>{


console.log(
"JARVIS LISTENING..."
);


updateActivity(
"LISTENING..."
);


};







recognition.onresult=(event)=>{


let command =
event.results[0][0].transcript;



console.log(
"VOICE COMMAND:",
command
);



updateActivity(
"COMMAND: "+command
);





if(
typeof jarvisThink==="function"
){


jarvisThink(
command
);


}



};







recognition.onerror=(e)=>{


console.log(
"VOICE ERROR",
e
);


};




}





function startJarvisListening(){


if(!recognition)

initJarvisVoice();



recognition.start();


}






function stopJarvisListening(){


if(recognition)

recognition.stop();


}




// ======================================
// AUTO LISTEN MODE
// ======================================


window.addEventListener(
"load",
()=>{


setTimeout(()=>{


if(typeof startJarvisListening==="function"){


startJarvisListening();


console.log(
"JARVIS AUTO VOICE ACTIVE"
);


}


},2000);


});


window.startJarvisListening=
startJarvisListening;



window.stopJarvisListening=
stopJarvisListening;




console.log(
"JARVIS VOICE ENGINE READY"
);