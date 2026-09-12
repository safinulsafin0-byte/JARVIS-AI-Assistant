// ======================================
// JARVIS 3D HOLOGRAM ENGINE v2
// Three.js + Gesture Control Ready
// ======================================


let scene;
let camera;
let renderer;


let core;
let rings = [];

let hologramGroup;


// Gesture controlled rotation
let targetRotationX = 0;
let targetRotationY = 0;

let currentRotationX = 0;
let currentRotationY = 0;





// ======================================
// INITIALIZE
// ======================================


function initJARVIS3D(){


    const canvas =
        document.getElementById(
            "hologramCanvas"
        );



    if(!canvas){

        console.error(
            "Hologram canvas missing"
        );

        return;

    }






    // SCENE

    scene =
        new THREE.Scene();






    // GROUP

    hologramGroup =
        new THREE.Group();


    scene.add(
        hologramGroup
    );







    // CAMERA

    camera =
        new THREE.PerspectiveCamera(

            45,

            canvas.clientWidth /
            canvas.clientHeight,

            0.1,

            1000

        );



    camera.position.z = 5;







    // RENDERER

    renderer =
        new THREE.WebGLRenderer({

            canvas:canvas,

            alpha:true,

            antialias:true

        });




    renderer.setPixelRatio(

        Math.min(
            window.devicePixelRatio,
            2
        )

    );



    resizeRenderer();






    createCore();

    createEnergyRings();






    animate();



}









// ======================================
// CREATE MAIN CORE
// ======================================


function createCore(){



    const geometry =

        new THREE.IcosahedronGeometry(

            1,

            2

        );





    const material =

        new THREE.MeshBasicMaterial({

            color:0x4fd7ff,

            wireframe:true,

            transparent:true,

            opacity:0.9

        });





    core =
        new THREE.Mesh(

            geometry,

            material

        );





    hologramGroup.add(
        core
    );



}









// ======================================
// ENERGY RINGS
// ======================================


function createEnergyRings(){



    for(
        let i = 0;
        i < 3;
        i++
    ){



        const ring =

            new THREE.Mesh(


                new THREE.TorusGeometry(

                    1.4 + i * 0.25,

                    0.012,

                    16,

                    120

                ),



                new THREE.MeshBasicMaterial({

                    color:0x4fd7ff,

                    transparent:true,

                    opacity:0.7

                })


            );





        ring.rotation.x =
            Math.PI / 2;




        ring.rotation.y =
            i * 0.5;




        rings.push(
            ring
        );



        hologramGroup.add(
            ring
        );


    }


}









// ======================================
// ANIMATION LOOP
// ======================================


function animate(){



    requestAnimationFrame(
        animate
    );







    // Core idle rotation


    if(core){


        core.rotation.x +=
            0.006;


        core.rotation.y +=
            0.010;



        const pulse =

            1 +

            Math.sin(
                Date.now()*0.002
            )
            *
            0.03;



        core.scale.set(

            pulse,

            pulse,

            pulse

        );


    }








    // Ring animation


    rings.forEach(

        (ring,index)=>{


            ring.rotation.z +=

                0.002 *
                (index+1);



        }

    );









    // Smooth gesture rotation


    if(hologramGroup){



        currentRotationX +=

            (
                targetRotationX -
                currentRotationX
            )
            *
            0.08;




        currentRotationY +=

            (
                targetRotationY -
                currentRotationY
            )
            *
            0.08;





        hologramGroup.rotation.x =
            currentRotationX;




        hologramGroup.rotation.y =
            currentRotationY;


    }








    renderer.render(

        scene,

        camera

    );



}









// ======================================
// GESTURE CONTROL
// ======================================


function rotateHologram(
    x,
    y
){



    targetRotationX =
        x;



    targetRotationY =
        y;



}









// ======================================
// PINCH SELECT EFFECT
// ======================================


function selectHologramObject(){



    if(!core)
        return;




    core.material.color.set(
        0x57e6a4
    );



    setTimeout(()=>{


        core.material.color.set(
            0x4fd7ff
        );


    },500);



}









// ======================================
// MENU ACTION
// ======================================


function openJarvisMenu(){



    console.log(

        "Opening JARVIS holographic menu"

    );



}









// ======================================
// STOP ACTION
// ======================================


function stopGestureAction(){



    targetRotationX = 0;

    targetRotationY = 0;



    console.log(

        "Gesture reset"

    );


}









// ======================================
// RESIZE
// ======================================


function resizeRenderer(){



    if(!renderer)
        return;



    const canvas =
        renderer.domElement;




    const width =
        canvas.clientWidth;



    const height =
        canvas.clientHeight;





    renderer.setSize(

        width,

        height,

        false

    );





    camera.aspect =
        width / height;



    camera.updateProjectionMatrix();



}









window.addEventListener(

    "resize",

    ()=>{


        resizeRenderer();


    }

);









window.addEventListener(

    "load",

    ()=>{


        initJARVIS3D();


    }

);