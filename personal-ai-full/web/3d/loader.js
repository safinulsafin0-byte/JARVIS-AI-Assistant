// ======================================
// JARVIS GLB / GLTF MODEL LOADER
// ======================================

let activeModel = null;


// ======================================
// LOAD MODEL
// ======================================

function loadJARVISModel(modelName){

    const modelInfo = getJARVISModel(modelName);

    if(!modelInfo){

        console.log(
            "Unknown JARVIS model:",
            modelName
        );

        return;
    }


    if(typeof THREE === "undefined"){

        console.log(
            "Three.js not loaded"
        );

        return;
    }


    if(typeof THREE.GLTFLoader === "undefined"){

        console.log(
            "GLTFLoader not loaded"
        );

        return;
    }


    const loader =
    new THREE.GLTFLoader();


    loader.load(

        modelInfo.path,


        function(gltf){


            if(activeModel){

                scene.remove(activeModel);

            }


            activeModel =
            gltf.scene;


            activeModel.scale.set(
                1.2,
                1.2,
                1.2
            );


            activeModel.position.set(
                0,
                0,
                0
            );


            scene.add(
                activeModel
            );


            console.log(
                "Loaded:",
                modelInfo.name
            );

        },


        function(progress){


            if(progress.total){

                const percent =

                (
                    progress.loaded /
                    progress.total
                ) * 100;


                console.log(
                    "Loading:",
                    percent.toFixed(0) + "%"
                );

            }

        },


        function(error){


            console.error(
                "Model loading failed:",
                error
            );

        }

    );

}