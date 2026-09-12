// ======================================
// JARVIS VOICE ENGINE v2
// ALWAYS ON MICROPHONE SYSTEM
// FINAL STABLE VERSION
// ======================================


let recognition = null;

let voiceActive = false;

let manualStop = false;


// ======================================
// INIT VOICE
// ======================================


function initVoice(){


console.log(
"INITIALIZING JARVIS VOICE"
);



const SpeechRecognition =

window.SpeechRecognition ||

window.webkitSpeechRecognition;



if(!SpeechRecognition){


console.error(
"Speech Recognition NOT SUPPORTED"
);


return;


}





recognition = new SpeechRecognition();



recognition.continuous = true;

recognition.interimResults = false;

recognition.lang = "en-US";





// ======================================
// START
// ======================================


recognition.onstart=function(){


voiceActive=true;

manualStop=false;



console.log(
"🎤 JARVIS ALWAYS LISTENING"
);



updateVoiceUI(

"LISTENING",

"waiting for command..."

);



};









// ======================================
// RESULT
// ======================================


recognition.onresult=function(event){



let result =

event.results[
event.results.length-1
];



let text =

result[0].transcript;



console.log(

"VOICE COMMAND:",

text

);






if(typeof setJarvisMode==="function"){


setJarvisMode(

"ai"

);


}





if(typeof jarvisThink==="function"){



jarvisThink(

text

);



}

else{


console.error(

"jarvisThink NOT FOUND"

);


}



};









// ======================================
// ERROR
// ======================================


recognition.onerror=function(event){



console.error(

"VOICE ERROR:",

event.error

);




if(event.error==="not-allowed"){



updateVoiceUI(

"MIC BLOCKED",

"allow microphone permission"

);



}




};









// ======================================
// AUTO RESTART
// ======================================


recognition.onend=function(){



console.log(

"VOICE ENDED"

);



voiceActive=false;




if(!manualStop){



setTimeout(()=>{



try{


recognition.start();



}

catch(e){



console.log(
"VOICE RESTART FAILED"
);


}



},500);



}



};









console.log(

"🔥 JARVIS VOICE ENGINE READY"

);



}









// ======================================
// START LISTENING
// ======================================


function startListening(){



manualStop=false;




if(!recognition){


initVoice();


}




try{


recognition.start();



}

catch(e){


console.log(

"VOICE ALREADY RUNNING"

);


}



}









// ======================================
// STOP
// ======================================


function stopListening(){



manualStop=true;


voiceActive=false;




if(recognition){


recognition.stop();


}




updateVoiceUI(

"STOPPED",

"microphone off"

);



}









// ======================================
// UI UPDATE
// ======================================


function updateVoiceUI(

title,

sub

){



let label =

document.getElementById(

"orbLabel"

);



let status =

document.getElementById(

"orbSub"

);




if(label){


label.innerText=title;


}




if(status){


status.innerText=sub;


}



}









// ======================================
// BUTTONS
// ======================================


window.addEventListener(

"load",

()=>{



let mic =

document.getElementById(

"micButton"

);



let stop =

document.getElementById(

"stopButton"

);






if(mic){


mic.onclick=function(){


startListening();


};



}





if(stop){


stop.onclick=function(){


stopListening();


};



}





// AUTO START

setTimeout(()=>{


startListening();


},1500);






console.log(

"VOICE BUTTON CONNECTED"

);



}

);









// ======================================
// EXPORT
// ======================================


window.initVoice =

initVoice;



window.startListening =

startListening;



window.stopListening =

stopListening;



console.log(

"🔥 JARVIS VOICE ENGINE v2 ALWAYS ON READY"

);