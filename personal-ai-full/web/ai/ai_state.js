// ======================================
// JARVIS AI STATE
// ======================================

window.JARVIS_MODE = "gesture";


function setJarvisMode(mode){

    window.JARVIS_MODE = mode;

    console.log(
        "JARVIS MODE:",
        mode
    );

}


function getJarvisMode(){

    return window.JARVIS_MODE;

}


window.setJarvisMode = setJarvisMode;
window.getJarvisMode = getJarvisMode;


console.log(
"JARVIS STATE READY"
);