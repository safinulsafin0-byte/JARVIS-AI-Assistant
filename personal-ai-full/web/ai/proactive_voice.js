// ======================================
// JARVIS PROACTIVE VOICE CONNECTOR v1
// EVENT -> VOICE
// ======================================


async function checkJarvisProactiveVoice(){


try{


const response = await fetch(
"http://127.0.0.1:8000/voice/get"
);



const data = await response.json();



if(
data.message &&
data.message.trim() !== ""
){


console.log(
"🔥 JARVIS AUTO RESPONSE:",
data.message
);




if(
typeof window.speakJarvis === "function"
){


await window.speakJarvis(
data.message
);



}

else{


console.error(
"speakJarvis function missing"
);


}


}



}

catch(error){


console.log(
"VOICE BRIDGE ERROR:",
error
);


}



}




// check every 3 seconds

setInterval(
checkJarvisProactiveVoice,
3000
);



console.log(
"🔥 PROACTIVE VOICE CONNECTOR READY"
);
