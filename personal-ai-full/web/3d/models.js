// ======================================
// JARVIS 3D MODEL REGISTRY
// ======================================

const JARVIS_MODELS = {

    reactor: {
        name: "Arc Reactor",
        path: "models/reactor.glb"
    },

    helmet: {
        name: "Iron Helmet",
        path: "models/helmet.glb"
    },

    brain: {
        name: "AI Brain",
        path: "models/brain.glb"
    }

};


// Get model info
function getJARVISModel(modelName){

    return JARVIS_MODELS[modelName] || null;

}