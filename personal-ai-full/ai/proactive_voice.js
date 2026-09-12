// ======================================
// JARVIS PROACTIVE VOICE LISTENER
// ======================================


async function checkJarvisVoice(){


try{


let res =
await fetch(
"http://127.0.0.1:5003/voice/get"
);


let data =
await res.json();



if(
data.message &&
data.message.length>0
){


console.log(
"JARVIS SPEAK:",
data.message
);



if(
typeof speakText==="function"
){

speakText(
data.message
);

}


}


}
catch(e){


console.log(
"Voice bridge offline"
);


}



}



setInterval(
checkJarvisVoice,
3000
);