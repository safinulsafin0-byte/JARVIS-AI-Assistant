// ==========================================
// JARVIS PARTICLE ENGINE v2
// Three.js Particle Workspace
// ==========================================


let particleSystem = null;

let particleGeometry = null;

let particleMaterial = null;


let particleActive = false;


let particlePositions = null;


const particleCount = 12000;







// ==========================================
// CREATE PARTICLES
// ==========================================


function createParticleSystem(){



    if(
        typeof hologramScene === "undefined"
    ){

        console.error(
            "Hologram scene missing"
        );

        return;

    }







    // remove old particles

    if(particleSystem){

        hologramScene.remove(
            particleSystem
        );

    }








    particleGeometry =
    new THREE.BufferGeometry();







    particlePositions =
    new Float32Array(

        particleCount * 3

    );








    for(
        let i=0;
        i<particleCount;
        i++
    ){



        const radius =
        Math.random()*3;



        const angle =
        Math.random()*Math.PI*2;





        particlePositions[i*3] =

        Math.cos(angle)
        *
        radius;




        particlePositions[i*3+1] =

        (
            Math.random()-0.5
        )
        *
        3;





        particlePositions[i*3+2] =

        Math.sin(angle)
        *
        radius;



    }







    particleGeometry.setAttribute(

        "position",

        new THREE.BufferAttribute(

            particlePositions,

            3

        )

    );








    particleMaterial =

    new THREE.PointsMaterial({


        color:0x00ffff,


        size:0.035,


        transparent:true,


        opacity:0.9,


        blending:
        THREE.AdditiveBlending


    });








    particleSystem =

    new THREE.Points(

        particleGeometry,

        particleMaterial

    );







    particleSystem.name =

    "JARVIS_PARTICLE_CORE";








    hologramScene.add(

        particleSystem

    );







    particleActive = true;







    updateParticleStatus(

        "PARTICLE MODE ACTIVE"

    );




    console.log(

        "JARVIS Particles Activated"

    );



}









// ==========================================
// REMOVE
// ==========================================


function removeParticles(){



    if(
        !particleSystem
    )

    return;





    if(
        typeof hologramScene !== "undefined"
    ){


        hologramScene.remove(

            particleSystem

        );


    }





    particleSystem=null;


    particleActive=false;



}









// ==========================================
// ANIMATION UPDATE
// Called from hologram core loop
// ==========================================


function updateParticles(){



    if(
        particleSystem &&
        particleActive
    ){



        particleSystem.rotation.y +=
        0.002;



        particleSystem.rotation.x +=
        0.001;



    }



}









// ==========================================
// HAND CONTROL
// ==========================================


function moveParticles(
x,
y
){



    if(
        !particleSystem
    )

    return;







    particleSystem.rotation.y +=

    x*0.05;





    particleSystem.rotation.x +=

    y*0.05;



}









// ==========================================
// SELECT EFFECT
// ==========================================


function selectParticleObject(){



    if(
        !particleMaterial
    )

    return;







    particleMaterial.size =
    0.07;







    setTimeout(()=>{


        if(particleMaterial){

            particleMaterial.size =
            0.035;

        }


    },300);



}









// ==========================================
// EXPORT
// ==========================================


window.createParticleSystem =
createParticleSystem;



window.removeParticles =
removeParticles;



window.updateParticles =
updateParticles;



window.moveParticles =
moveParticles;



window.selectParticleObject =
selectParticleObject;








// ==========================================
// UI
// ==========================================


function updateParticleStatus(text){



    const ids=[

        "currentMode",

        "workspaceTitle",

        "modeText"

    ];





    ids.forEach(id=>{


        const el =
        document.getElementById(id);



        if(el){

            el.innerText=text;

        }



    });



}