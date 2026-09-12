async function getSystemStatus(){


let res =
await fetch(
"http://127.0.0.1:5050/status"
);



let data =
await res.json();



console.log(
"JARVIS SYSTEM:",
data
);



return data;


}

window.getSystemStatus=
getSystemStatus;