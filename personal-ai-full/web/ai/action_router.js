// ======================================
// JARVIS AI ACTION ROUTER v5
// BEAST MODE
// 3D + DRAWING + PARTICLES + HAND
// SYSTEM MONITOR + ERROR SAFE ROUTING
// ======================================


async function executeAIAction(action){

    console.log(
        "🔥 AI ACTION RECEIVED:",
        action
    );


    // ======================================
    // VALIDATION
    // ======================================

    if(
        !action ||
        typeof action !== "object" ||
        !action.intent
    ){

        console.error(
            "❌ INVALID AI ACTION:",
            action
        );

        return {
            success:false,
            error:"invalid_action"
        };
    }


    try{


        switch(action.intent){


            // ======================================
            // WORKSPACE
            // ======================================

            case "open_workspace":{

                console.log(
                    "OPEN WORKSPACE:",
                    action.workspace
                );


                if(
                    typeof window.openHologramWorkspace
                    === "function"
                ){

                    window.openHologramWorkspace(
                        action.workspace
                    );

                }
                else{

                    console.error(
                        "❌ openHologramWorkspace missing"
                    );

                }


                return {
                    success:true,
                    intent:action.intent
                };
            }



            // ======================================
            // AI DRAWING
            // ======================================

            case "create_art":{

                console.log(
                    "🎨 AI DRAW REQUEST:",
                    action.prompt
                );


                if(
                    typeof window.handleAIDrawing
                    === "function"
                ){

                    await Promise.resolve(
                        window.handleAIDrawing(
                            action.prompt || ""
                        )
                    );

                }
                else{

                    console.error(
                        "❌ Drawing Agent missing"
                    );

                }


                return {
                    success:true,
                    intent:action.intent
                };
            }



            // ======================================
            // BASIC DRAW
            // ======================================

            case "draw_shape":{

                console.log(
                    "DRAW SHAPE:",
                    action.shape
                );


                if(
                    typeof window.drawAIShape
                    === "function"
                ){

                    await Promise.resolve(
                        window.drawAIShape(
                            action.shape || "custom",
                            action.prompt || ""
                        )
                    );

                }

                else if(
                    typeof window.handleAIDrawing
                    === "function"
                ){

                    await Promise.resolve(
                        window.handleAIDrawing(
                            action.prompt ||
                            `draw ${action.shape || "object"}`
                        )
                    );

                }

                else{

                    console.error(
                        "❌ Drawing system missing"
                    );

                }


                return {
                    success:true,
                    intent:action.intent
                };
            }



            // ======================================
            // LOAD 3D MODEL
            // ======================================

            case "load_model":{

                console.log(
                    "LOAD MODEL:",
                    action.model
                );


                if(
                    typeof window.loadAIModel
                    === "function"
                ){

                    await Promise.resolve(
                        window.loadAIModel(
                            action.model
                        )
                    );

                }
                else{

                    console.error(
                        "❌ loadAIModel missing"
                    );

                }


                return {
                    success:true,
                    intent:action.intent
                };
            }



            // ======================================
            // PARTICLE CONTROL
            // ======================================

            case "particle_control":{

                console.log(
                    "PARTICLE COMMAND:",
                    action.command
                );


                switch(action.command){


                    case "explode":

                        if(
                            typeof window.hologramExplosion
                            === "function"
                        ){

                            window.hologramExplosion();

                        }

                        break;



                    case "clear":

                        if(
                            typeof window.hologramClear
                            === "function"
                        ){

                            window.hologramClear();

                        }

                        break;



                    case "hand_follow":

                    case "follow":

                        if(
                            typeof window.enableHandFollow
                            === "function"
                        ){

                            window.enableHandFollow();

                        }
                        else{

                            console.warn(
                                "⚠️ Hand follow not connected"
                            );

                        }

                        break;



                    case "freeze":

                        if(
                            typeof window.freezeParticles
                            === "function"
                        ){

                            window.freezeParticles();

                        }
                        else{

                            console.warn(
                                "⚠️ freezeParticles missing"
                            );

                        }

                        break;



                    default:

                        console.warn(
                            "⚠️ UNKNOWN PARTICLE COMMAND:",
                            action.command
                        );

                }


                return {
                    success:true,
                    intent:action.intent
                };
            }



            // ======================================
            // TRANSFORM
            // ======================================

            case "transform":{

                console.log(
                    "TRANSFORM:",
                    action.action
                );


                switch(action.action){


                    case "rotate":

                        if(
                            typeof window.rotate3D
                            === "function"
                        ){

                            window.rotate3D();

                        }

                        break;



                    case "rotate_fast":

                        if(
                            typeof window.setRotationSpeed
                            === "function"
                        ){

                            window.setRotationSpeed(
                                0.08
                            );

                        }

                        break;



                    case "rotate_slow":

                        if(
                            typeof window.setRotationSpeed
                            === "function"
                        ){

                            window.setRotationSpeed(
                                0.01
                            );

                        }

                        break;



                    case "scale_up":

                        if(
                            typeof window.scale3DObject
                            === "function"
                        ){

                            window.scale3DObject(
                                1.5
                            );

                        }

                        break;



                    case "scale_down":

                        if(
                            typeof window.scale3DObject
                            === "function"
                        ){

                            window.scale3DObject(
                                0.5
                            );

                        }

                        break;



                    case "reset":

                        if(
                            typeof window.resetHologram
                            === "function"
                        ){

                            window.resetHologram();

                        }

                        break;



                    default:

                        console.warn(
                            "⚠️ UNKNOWN TRANSFORM:",
                            action.action
                        );

                }


                return {
                    success:true,
                    intent:action.intent
                };
            }



            // ======================================
            // COLOR CONTROL
            // ======================================

            case "change_color":{

                console.log(
                    "CHANGE COLOR:",
                    action.color
                );


                if(
                    typeof window.changeHologramColor
                    === "function"
                ){

                    window.changeHologramColor(
                        action.color
                    );

                }
                else{

                    console.warn(
                        "⚠️ Color engine missing"
                    );

                }


                return {
                    success:true,
                    intent:action.intent
                };
            }



            // ======================================
            // HAND CONTROL
            // ======================================

            case "hand_control":{

                console.log(
                    "HAND MODE:",
                    action.mode
                );


                if(
                    typeof window.enableHandControl
                    === "function"
                ){

                    window.enableHandControl(
                        action.mode
                    );

                }
                else{

                    console.warn(
                        "⚠️ Hand control missing"
                    );

                }


                return {
                    success:true,
                    intent:action.intent
                };
            }



            // ======================================
            // SYSTEM MONITOR
            // CPU / RAM / GPU / BATTERY
            // ======================================

            case "system_monitor":
            case "system_status":{

                console.log(
                    "🖥️ JARVIS SYSTEM MONITOR REQUEST"
                );


                if(
                    typeof window.getSystemStatus
                    !== "function"
                ){

                    console.error(
                        "❌ getSystemStatus missing"
                    );


                    updateSystemActivity(
                        "System monitor is not connected."
                    );


                    return {
                        success:false,
                        error:"system_monitor_missing"
                    };
                }


                const status =
                    await window.getSystemStatus();


                console.log(
                    "🖥️ SYSTEM STATUS:",
                    status
                );


                if(!status){

                    console.error(
                        "❌ Empty system status"
                    );


                    return {
                        success:false,
                        error:"empty_system_status"
                    };
                }


                const message =
                    buildSystemStatusMessage(
                        status
                    );


                console.log(
                    "JARVIS:",
                    message
                );


                updateSystemActivity(
                    message
                );


                speakJarvisResponse(
                    message
                );


                return {
                    success:true,
                    intent:action.intent,
                    data:status,
                    message:message
                };
            }



            // ======================================
            // SYSTEM CONTROL
            // ======================================

            case "system_control":{

                console.log(
                    "SYSTEM:",
                    action.command
                );


                switch(action.command){


                    case "clear":

                        if(
                            typeof window.hologramClear
                            === "function"
                        ){

                            window.hologramClear();

                        }


                        if(
                            typeof window.clear3DObjects
                            === "function"
                        ){

                            window.clear3DObjects();

                        }

                        break;



                    case "reset":

                        if(
                            typeof window.resetHologram
                            === "function"
                        ){

                            window.resetHologram();

                        }

                        break;



                    case "status":

                        return await executeAIAction({

                            intent:"system_monitor"

                        });



                    default:

                        console.warn(
                            "⚠️ UNKNOWN SYSTEM COMMAND:",
                            action.command
                        );

                }


                return {
                    success:true,
                    intent:action.intent
                };
            }



            // ======================================
            // UNKNOWN
            // ======================================

            case "unknown":{

                console.warn(
                    "⚠️ JARVIS COULD NOT UNDERSTAND:",
                    action.text
                );


                return {
                    success:false,
                    error:"unknown_command",
                    action:action
                };
            }



            default:{

                console.warn(
                    "⚠️ UNKNOWN INTENT:",
                    action.intent,
                    action
                );


                return {
                    success:false,
                    error:"unknown_intent",
                    intent:action.intent
                };
            }

        }


    }
    catch(error){


        console.error(
            "❌ JARVIS ACTION ROUTER ERROR:",
            error
        );


        updateSystemActivity(
            "JARVIS action error."
        );


        return {
            success:false,
            error:
                error?.message ||
                String(error)
        };

    }

}



// ======================================
// BUILD SYSTEM STATUS MESSAGE
// ======================================

function buildSystemStatusMessage(status){


    const parts=[];


    if(
        status.cpu !== undefined &&
        status.cpu !== null
    ){

        parts.push(
            `CPU ${Math.round(Number(status.cpu))} percent`
        );

    }


    if(
        status.ram !== undefined &&
        status.ram !== null
    ){

        parts.push(
            `RAM ${Math.round(Number(status.ram))} percent`
        );

    }


    if(
        Array.isArray(status.gpu) &&
        status.gpu.length > 0
    ){

        const gpu=status.gpu[0];


        if(
            gpu.load !== undefined &&
            gpu.load !== null
        ){

            parts.push(
                `GPU ${Math.round(Number(gpu.load))} percent`
            );

        }

    }

    else if(
        status.gpu_percent !== undefined
    ){

        parts.push(
            `GPU ${Math.round(Number(status.gpu_percent))} percent`
        );

    }


    if(
        status.battery !== undefined &&
        status.battery !== null
    ){

        parts.push(
            `Battery ${Math.round(Number(status.battery))} percent`
        );

    }


    if(parts.length===0){

        return "System monitor is online, but no hardware data was returned.";

    }


    return "System status. " +
        parts.join(". ") +
        ".";

}



// ======================================
// UPDATE JARVIS UI
// ======================================

function updateSystemActivity(message){


    const activity =
        document.getElementById(
            "activityText"
        );


    if(activity){

        activity.textContent=message;

    }



    const orbSub =
        document.getElementById(
            "orbSub"
        );


    if(orbSub){

        orbSub.textContent=message;

    }

}



// ======================================
// OPTIONAL VOICE RESPONSE BRIDGE
// ======================================

function speakJarvisResponse(message){


    /*
        Your existing offline Piper TTS should remain
        the preferred voice engine.

        This router only calls an existing TTS function.
    */


    if(
        typeof window.speakText
        === "function"
    ){

        window.speakText(message);
        return;

    }


    if(
        typeof window.jarvisSpeak
        === "function"
    ){

        window.jarvisSpeak(message);
        return;

    }


    if(
        typeof window.speak
        === "function"
    ){

        window.speak(message);

    }

}



// ======================================
// EXPORTS
// ======================================

window.executeAIAction =
    executeAIAction;


window.buildSystemStatusMessage =
    buildSystemStatusMessage;


window.updateSystemActivity =
    updateSystemActivity;


console.log(
    "🔥 JARVIS ACTION ROUTER v5 SYSTEM MONITOR BEAST MODE READY"
);