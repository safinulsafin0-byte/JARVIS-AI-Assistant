const vscode = require("vscode");


function activate(context) {


    console.log(" JARVIS Extension Activated");


    const provider =
        vscode.window.registerWebviewViewProvider(

            "jarvis.chat",

            {

                resolveWebviewView(webviewView) {


                    webviewView.webview.options = {

                        enableScripts: true

                    };


                    webviewView.webview.html = `

<!DOCTYPE html>

<html>

<body>

<h2>JARVIS</h2>


<textarea
id="input"
style="width:100%;height:90px;"
placeholder="Ask JARVIS..."
></textarea>


<br><br>


<button id="sendBtn">
Send
</button>


<pre
id="output"
style="white-space:pre-wrap;"
></pre>



<script>

console.log(" JARVIS WEBVIEW LOADED");


const input = document.getElementById("input");
const output = document.getElementById("output");
const button = document.getElementById("sendBtn");



async function send(){


    console.log(" SEND CLICKED");


    const text = input.value.trim();


    if(!text){

        output.textContent =
        "Please type something.";

        return;

    }



    output.textContent =
    " JARVIS thinking...";



    console.log(
        "Sending:",
        text
    );



    try{


        const response = await fetch(

            "http://127.0.0.1:8000/jarvis/code",

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },


                body:JSON.stringify({

                    message:text,

                    file:"vscode",

                    code:""

                })

            }

        );



        console.log(
            "STATUS:",
            response.status
        );



        const data =
        await response.json();



        console.log(
            "RESPONSE:",
            data
        );



        if(data.success){


            output.textContent =

            JSON.stringify(

                data.answer,

                null,

                2

            );


        }

        else{


            output.textContent =

            "ERROR: "

            +

            data.error;


        }



    }

    catch(error){


        console.error(
            "FETCH ERROR:",
            error
        );


        output.textContent =

        "Cannot connect to JARVIS API\n\n"

        +

        error.message;


    }


}



button.addEventListener(

    "click",

    send

);



console.log(" BUTTON CONNECTED");


</script>


</body>

</html>

`;

                }

            }

        );



    context.subscriptions.push(

        provider

    );


}



function deactivate(){}



module.exports = {

    activate,

    deactivate

};