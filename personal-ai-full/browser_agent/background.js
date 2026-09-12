let currentPage={

url:"",
title:"",
time:0

};



chrome.tabs.onActivated.addListener(
async(info)=>{


let tab =
await chrome.tabs.get(
info.tabId
);



updatePage(tab);


});





chrome.tabs.onUpdated.addListener(
async(tabId,change,tab)=>{


if(tab.active){

updatePage(tab);

}


});







function updatePage(tab){


if(!tab.url)
return;



currentPage={

url:tab.url,

title:tab.title,

time:Date.now()

};




fetch(
"http://127.0.0.1:5051/browser",
{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:
JSON.stringify(currentPage)


}

);


}