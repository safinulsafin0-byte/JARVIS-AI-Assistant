// JARVIS HOLOGRAM EFFECTS

function jarvisSpeakMode(){

    if(core){

        core.material.color.set(
            0x57e6a4
        );

    }

}



function jarvisIdleMode(){

    if(core){

        core.material.color.set(
            0x00ffff
        );

    }

}// ======================================
// JARVIS HOLOGRAM VISUAL EFFECTS
// ======================================


let particles;
let scanRing;





// ======================================
// CREATE HOLOGRAM EFFECT
// ======================================


function createHologramEffects(){


    if(!scene){

        console.log(
            "JARVIS scene not ready"
        );

        return;

    }






    // ===============================
    // PARTICLE FIELD
    // ===============================


    const particleGeometry =

    new THREE.BufferGeometry();



    const particleCount = 300;



    const positions = [];





    for(
        let i = 0;
        i < particleCount;
        i++
    ){


        positions.push(

            (Math.random()-0.5)*5,

            (Math.random()-0.5)*5,

            (Math.random()-0.5)*5

        );


    }






    particleGeometry.setAttribute(

        "position",

        new THREE.Float32BufferAttribute(

            positions,

            3

        )

    );







    const particleMaterial =

    new THREE.PointsMaterial({

        color:0x4fd7ff,

        size:0.025,

        transparent:true,

        opacity:0.7

    });






    particles = new THREE.Points(

        particleGeometry,

        particleMaterial

    );





    scene.add(particles);









    // ===============================
    // SCAN RING
    // ===============================



    scanRing = new THREE.Mesh(


        new THREE.TorusGeometry(

            1.8,

            0.008,

            16,

            120

        ),



        new THREE.MeshBasicMaterial({

            color:0x57e6a4,

            transparent:true,

            opacity:0.5

        })


    );





    scanRing.rotation.x =

    Math.PI/2;





    scene.add(scanRing);



}









// ======================================
// HOLOGRAM ANIMATION
// ======================================


function animateHologram(){



    if(particles){



        particles.rotation.y +=0.0015;


        particles.rotation.x +=0.0008;


    }






    if(scanRing){


        scanRing.rotation.z +=0.01;



        let scale =

        1 +

        Math.sin(

            Date.now()*0.003

        )*0.15;



        scanRing.scale.set(

            scale,

            scale,

            scale

        );



    }





}









// ======================================
// JARVIS STATES
// ======================================


function jarvisSpeaking(){


    if(core){


        core.material.color.set(

            0x57e6a4

        );


    }


}





function jarvisIdle(){


    if(core){


        core.material.color.set(

            0x4fd7ff

        );


    }


}








// ======================================
// CONNECT WITH ENGINE
// ======================================


window.addEventListener(

"load",

()=>{


    setTimeout(()=>{


        createHologramEffects();


    },500);



});
