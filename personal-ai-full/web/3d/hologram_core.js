// ==========================================
// JARVIS HOLOGRAM CORE ENGINE v2
// Three.js Main Renderer
// ==========================================


let hologramScene;

let hologramCamera;

let hologramRenderer;

let hologramClock;


let hologramObjects = [];






// ==========================================
// INIT
// ==========================================


function initHologramCore(){



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






    hologramScene =
    new THREE.Scene();






    const width =
    canvas.clientWidth ||
    window.innerWidth;


    const height =
    canvas.clientHeight ||
    window.innerHeight;







    hologramCamera =
    new THREE.PerspectiveCamera(

        45,

        width/height,

        0.1,

        1000

    );






    hologramCamera.position.set(

        0,

        0,

        6

    );







    hologramRenderer =
    new THREE.WebGLRenderer({

        canvas,

        alpha:true,

        antialias:true

    });






    hologramRenderer.setPixelRatio(
        window.devicePixelRatio
    );





    hologramRenderer.setSize(

        width,

        height

    );






    hologramClock =
    new THREE.Clock();







    createEnvironment();



    animateHologram();






    console.log(
        "JARVIS Hologram Core Online"
    );



}









// ==========================================
// ENVIRONMENT
// ==========================================


function createEnvironment(){



    const grid =

    new THREE.GridHelper(

        20,

        40,

        0x00ffff,

        0x003333

    );



    grid.position.y=-1.5;



    hologramScene.add(grid);






    const geometry =

    new THREE.IcosahedronGeometry(

        0.8,

        2

    );





    const material =

    new THREE.MeshBasicMaterial({

        color:0x00ffff,

        wireframe:true

    });





    const core =

    new THREE.Mesh(

        geometry,

        material

    );






    core.name =
    "JARVIS_CORE";





    hologramScene.add(core);



    hologramObjects.push(core);



}









// ==========================================
// OBJECT MANAGEMENT
// ==========================================


function addHologramObject(obj){



    if(!obj)
        return;



    if(
        !hologramObjects.includes(obj)
    ){

        hologramObjects.push(obj);

    }




}



window.addHologramObject =
addHologramObject;









function clearHologram(){



    hologramObjects.forEach(

        obj=>{


            if(
                obj.name !==
                "JARVIS_CORE"
            ){


                if(
                    obj.parent
                ){

                    obj.parent.remove(
                        obj
                    );

                }


            }



        }

    );




    hologramObjects =

    hologramObjects.filter(

        obj=>

        obj.name==="JARVIS_CORE"

    );




    if(
        typeof removeParticles==="function"
    ){

        removeParticles();

    }



}



window.clearHologram =
clearHologram;









// ==========================================
// GESTURE ROTATION
// ==========================================


function rotateHologram(x,y){



    hologramObjects.forEach(

        obj=>{


            obj.rotation.x=x;


            obj.rotation.y=y;


        }

    );



}


window.rotateHologram =
rotateHologram;









// ==========================================
// ANIMATION LOOP
// ==========================================


function animateHologram(){



    requestAnimationFrame(

        animateHologram

    );






    if(
        typeof updateParticles==="function"
    ){

        updateParticles();

    }







    hologramObjects.forEach(

        obj=>{


            if(
                obj.name==="JARVIS_CORE"
            ){


                obj.rotation.y+=0.01;


                obj.rotation.x+=0.005;


            }



        }

    );







    if(

        hologramRenderer &&

        hologramScene &&

        hologramCamera

    ){


        hologramRenderer.render(

            hologramScene,

            hologramCamera

        );


    }



}









// ==========================================
// RESIZE
// ==========================================


window.addEventListener(

"resize",

()=>{


    if(!hologramCamera)
        return;





    const canvas =
    document.getElementById(
        "hologramCanvas"
    );



    const width =
    canvas.clientWidth;


    const height =
    canvas.clientHeight;





    hologramCamera.aspect =
    width/height;



    hologramCamera.updateProjectionMatrix();




    hologramRenderer.setSize(

        width,

        height

    );



});









// ==========================================
// START
// ==========================================


window.addEventListener(

"load",

()=>{


    initHologramCore();


});