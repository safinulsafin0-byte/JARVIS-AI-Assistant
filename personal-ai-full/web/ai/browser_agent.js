async function getCurrentPage(){


let res =
await fetch(
"http://127.0.0.1:5051/browser/status"
);


let data =
await res.json();


console.log(
"CURRENT PAGE:",
data
);


return data;


}



window.getCurrentPage =
getCurrentPage;