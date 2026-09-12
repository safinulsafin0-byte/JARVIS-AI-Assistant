/* ============================================================
   JARVIS AI OFFICE
   FULL OFFLINE ALWAYS-ON APP.JS
   ============================================================

   CORE FLOW:

   NORMAL TEXT
   INPUT
      ↓
   sendCommand()
      ↓
   /api/chat
      ↓
   JARVIS RESPONSE
      ↓
   CHAT UI
      +
   /api/speak
      ↓
   Piper

   VISUAL / 3D COMMAND
   INPUT
      ↓
   sendCommand()
      ↓
   jarvisThink()
      ↓
   action_router
      ↓
   3D / Hologram / DNA
      ↓
   JARVIS UI
      +
   /api/speak

   VOICE
   Microphone
      ↓
   MediaRecorder
      ↓
   /api/transcribe
      ↓
   transcript
      ↓
   sendCommand()
      ↓
   same pipeline

   ============================================================ */

"use strict";

/* ============================================================
   ENDPOINTS
============================================================ */

const CHAT_ENDPOINT = "/api/chat";
const TRANSCRIBE_ENDPOINT = "/api/transcribe";
const SPEAK_ENDPOINT = "/api/speak";
const SPEAK_STOP_ENDPOINT = "/api/speak/stop";

/* ============================================================
   OFFICE CONFIG
============================================================ */

const ROLE_COLORS = {
    coordinator: "#4fd7ff",
    research: "#57e6a4",
    vision: "#f7c96c",
    image: "#9b8bff",
    tool: "#ff8bd0"
};

const WORKERS = {
    coordinator: {
        name: "Coordinator",
        activity: "Command Planning"
    },

    research: {
        name: "Research Agent",
        activity: "Information Search"
    },

    vision: {
        name: "Vision Agent",
        activity: "Image Analysis"
    },

    image: {
        name: "Image Agent",
        activity: "Image Generation"
    },

    tool: {
        name: "Tool Agent",
        activity: "System Actions"
    }
};

/* ============================================================
   DOM
============================================================ */

const userInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const micButton =
    document.getElementById("micButton");

const stopButton =
    document.getElementById("stopButton");

const gestureButton =
    document.getElementById("gestureButton");

const chatSection =
    document.getElementById("chat");

const welcomeMessage =
    document.getElementById("welcome");

const activityText =
    document.getElementById("activityText");

const orbLabel =
    document.getElementById("orbLabel");

const orbSub =
    document.getElementById("orbSub");

const tagLayer =
    document.getElementById("tagLayer");

const officeCanvas =
    document.getElementById("officeCanvas");

const orbCanvas =
    document.getElementById("orbCanvas");

const attachmentInput =
    document.getElementById("attachment-input");

const attachmentButton =
    document.getElementById("attachment-btn");

const attachmentPreview =
    document.getElementById("attachment-preview");

const octx =
    officeCanvas
        ? officeCanvas.getContext("2d")
        : null;

const octx2 =
    orbCanvas
        ? orbCanvas.getContext("2d")
        : null;

if (octx) {
    octx.imageSmoothingEnabled = false;
}

/* ============================================================
   STATE
============================================================ */

let selectedAttachment = null;

let isProcessing = false;

let isSpeaking = false;

let ttsRequestInProgress = false;

let currentAbortController = null;

let currentTTSId = 0;

let systemState = "idle";

let alwaysListening = true;

let mediaStream = null;

let mediaRecorder = null;

let recordedChunks = [];

let isRecordingVoice = false;

let microphoneBusy = false;

let discardCurrentRecording = false;

let voiceRestartTimer = null;

let voiceChunkTimer = null;

let gestureActive = false;

let pendingConfirmationCommand = null;

const VOICE_CHUNK_SECONDS = 4;

/* ============================================================
   CONFIRMATION
============================================================ */

const CONFIRM_WORDS = new Set([
    "yes",
    "y",
    "yeah",
    "yep",
    "confirm",
    "confirmed",
    "do it",
    "go ahead",
    "proceed",
    "sure",
    "ok",
    "okay"
]);

const DENY_WORDS = new Set([
    "no",
    "n",
    "nope",
    "cancel",
    "stop",
    "don't",
    "dont",
    "never mind",
    "nevermind"
]);

function looksLikeConfirmReply(text) {
    return CONFIRM_WORDS.has(
        normalizeText(text).toLowerCase()
    );
}

function looksLikeDenyReply(text) {
    return DENY_WORDS.has(
        normalizeText(text).toLowerCase()
    );
}

/* ============================================================
   HELPERS
============================================================ */

function sleep(ms) {
    return new Promise(resolve => {
        setTimeout(resolve, ms);
    });
}

function normalizeText(text) {
    return String(text || "")
        .trim()
        .replace(/\s+/g, " ");
}

function safeSetText(element, text) {
    if (!element) {
        return;
    }

    element.textContent =
        String(text ?? "");
}

/* ============================================================
   SYSTEM STATE
============================================================ */

function setSystemState(
    state,
    subText
) {
    systemState = state;

    let label = "SYSTEM ACTIVE";

    if (state === "thinking") {
        label = "THINKING";
    }

    else if (state === "speaking") {
        label = "SPEAKING";
    }

    else if (state === "listening") {
        label = "LISTENING";
    }

    safeSetText(
        orbLabel,
        label
    );

    safeSetText(
        orbSub,
        subText ||
        (
            state === "thinking"
                ? "processing..."
                : state === "speaking"
                    ? "offline Piper voice..."
                    : state === "listening"
                        ? "always listening..."
                        : "idle"
        )
    );
}

/* ============================================================
   TOOL RESULT
============================================================ */

function simplifyToolAnswer(answer) {

    const text =
        String(answer || "").trim();

    if (
        /^SUCCESS\s*:/i.test(text) ||
        /^SUCCESS\b/i.test(text)
    ) {
        return "Success";
    }

    return answer;
}

/* ============================================================
   ATTACHMENTS
============================================================ */

const DOCUMENT_EXTENSIONS = [
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".csv",
    ".md",
    ".rtf",
    ".xlsx",
    ".xls",
    ".ppt",
    ".pptx"
];

function isImageAttachment(
    attachment
) {
    if (!attachment) {
        return false;
    }

    if (
        attachment.type &&
        attachment.type.startsWith("image/")
    ) {
        return true;
    }

    const name =
        String(
            attachment.name || ""
        ).toLowerCase();

    return [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".bmp"
    ].some(
        ext => name.endsWith(ext)
    );
}

function isDocumentAttachment(
    attachment
) {
    if (!attachment) {
        return false;
    }

    const name =
        String(
            attachment.name || ""
        ).toLowerCase();

    if (
        DOCUMENT_EXTENSIONS.some(
            ext => name.endsWith(ext)
        )
    ) {
        return true;
    }

    const type =
        attachment.type || "";

    return (
        type === "application/pdf" ||
        type === "application/msword" ||
        type.startsWith(
            "application/vnd.openxmlformats-officedocument"
        ) ||
        type.startsWith("text/") ||
        type.includes("spreadsheet") ||
        type.includes("presentation")
    );
}

/* ============================================================
   WORKER DETECTION
============================================================ */

function detectWorker(
    command,
    attachment
) {
    const text =
        normalizeText(command)
            .toLowerCase();

    if (
        attachment &&
        isImageAttachment(attachment)
    ) {
        return "vision";
    }

    if (
        attachment &&
        isDocumentAttachment(attachment)
    ) {
        return "research";
    }

    if (
        [
            "generate image",
            "create image",
            "make image",
            "draw an image",
            "draw me",
            "generate a picture",
            "create a picture",
            "make a picture",
            "image generation"
        ].some(
            key => text.includes(key)
        )
    ) {
        return "image";
    }

    if (
        [
            "youtube",
            "browser",
            "open chrome",
            "website",
            "web",
            "play video",
            "pause video",
            "resume video",
            "stop video",
            "search youtube",
            "open youtube",
            "open ",
            "delete ",
            "remove file",
            "create folder",
            "save file"
        ].some(
            key => text.includes(key)
        )
    ) {
        return "tool";
    }

    if (
        /\bsearch\b/i.test(text)
    ) {
        return "tool";
    }

    return "research";
}

/* ============================================================
   CHAT UI
============================================================ */

function addChatMessage(
    sender,
    message
) {
    if (!chatSection) {
        return null;
    }

    if (welcomeMessage) {
        welcomeMessage.style.display =
            "none";
    }

    const element =
        document.createElement("div");

    element.className =
        `chat-message ${sender}-message`;

    const senderName =
        sender === "user"
            ? "YOU"
            : "JARVIS";

    const avatar =
        sender === "user"
            ? "U"
            : "J";

    element.innerHTML = `
        <div class="chat-message-avatar">
            ${avatar}
        </div>

        <div class="chat-message-content">

            <div class="chat-message-name">
                ${senderName}
            </div>

            <div class="chat-message-text"></div>

        </div>
    `;

    const textElement =
        element.querySelector(
            ".chat-message-text"
        );

    if (textElement) {
        textElement.textContent =
            String(message || "");
    }

    chatSection.appendChild(
        element
    );

    element.scrollIntoView({
        behavior: "smooth",
        block: "end"
    });

    return element;
}

function addTypingMessage() {

    if (!chatSection) {
        return null;
    }

    const element =
        document.createElement("div");

    element.className =
        "chat-message jarvis-message typing-message";

    element.innerHTML = `
        <div class="chat-message-avatar">
            J
        </div>

        <div class="chat-message-content">

            <div class="chat-message-name">
                JARVIS
            </div>

            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>

        </div>
    `;

    chatSection.appendChild(
        element
    );

    element.scrollIntoView({
        behavior: "smooth",
        block: "end"
    });

    return element;
}

function removeTypingMessage(
    element
) {
    if (
        element &&
        element.parentNode
    ) {
        element.remove();
    }
}

/* ============================================================
   ATTACHMENT UI
============================================================ */

function showAttachmentPreview(
    file
) {
    if (!attachmentPreview) {
        return;
    }

    attachmentPreview.innerHTML =
        "";

    attachmentPreview.style.display =
        "flex";

    const item =
        document.createElement("div");

    item.className =
        "attachment-preview-item";

    const name =
        document.createElement("span");

    name.className =
        "attachment-file-name";

    name.textContent =
        `Attachment: ${file.name}`;

    const remove =
        document.createElement("button");

    remove.type =
        "button";

    remove.className =
        "remove-attachment";

    remove.textContent =
        "×";

    remove.addEventListener(
        "click",
        removeAttachment
    );

    item.appendChild(name);

    item.appendChild(remove);

    attachmentPreview.appendChild(
        item
    );
}

function removeAttachment() {

    selectedAttachment =
        null;

    if (attachmentInput) {
        attachmentInput.value =
            "";
    }

    if (attachmentPreview) {

        attachmentPreview.innerHTML =
            "";

        attachmentPreview.style.display =
            "none";
    }
}

if (
    attachmentButton &&
    attachmentInput
) {
    attachmentButton.addEventListener(
        "click",
        () => {
            attachmentInput.click();
        }
    );
}

if (attachmentInput) {

    attachmentInput.addEventListener(
        "change",
        event => {

            const file =
                event.target.files &&
                event.target.files[0];

            if (!file) {
                return;
            }

            selectedAttachment =
                file;

            showAttachmentPreview(
                file
            );

            safeSetText(
                activityText,
                `Attachment selected: ${file.name}`
            );
        }
    );
}

/* ============================================================
   PIPER TEXT CLEANER
============================================================ */

function cleanTextForSpeech(
    text
) {
    return String(text || "")

        .replace(
            /```[\s\S]*?```/g,
            "Code block omitted."
        )

        .replace(
            /`([^`]+)`/g,
            "$1"
        )

        .replace(
            /^#{1,6}\s+/gm,
            ""
        )

        .replace(
            /\*\*/g,
            ""
        )

        .replace(
            /__/g,
            ""
        )

        .replace(
            /\*/g,
            ""
        )

        .replace(
            /https?:\/\/\S+/gi,
            "website"
        )

        .replace(
            /\n+/g,
            ". "
        )

        .replace(
            /\s+/g,
            " "
        )

        .trim();
}

/* ============================================================
   STOP PIPER
============================================================ */

async function stopJarvisVoice() {

    currentTTSId += 1;

    try {

        await fetch(
            SPEAK_STOP_ENDPOINT,
            {
                method: "POST",
                cache: "no-store"
            }
        );

    } catch (_) {}

    isSpeaking =
        false;

    ttsRequestInProgress =
        false;
}

/* ============================================================
   JARVIS PIPER VOICE
============================================================ */

async function speakJarvis(
    text
) {
    const speechText =
        cleanTextForSpeech(
            text
        );

    if (!speechText) {
        resumeAlwaysOnMicrophone();
        return;
    }

    const thisTTSId =
        ++currentTTSId;

    pauseAlwaysOnMicrophone();

    isSpeaking =
        true;

    ttsRequestInProgress =
        true;

    safeSetText(
        activityText,
        "JARVIS is speaking..."
    );

    setSystemState(
        "speaking",
        "offline Piper voice..."
    );

    try {

        const response =
            await fetch(
                SPEAK_ENDPOINT,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            text:
                                speechText
                        }),

                    cache: "no-store"
                }
            );

        const rawText =
            await response.text();

        let data;

        try {

            data =
                JSON.parse(
                    rawText
                );

        } catch (_) {

            throw new Error(
                "Invalid offline TTS response."
            );
        }

        if (
            !response.ok ||
            data.success === false
        ) {

            throw new Error(
                data.error ||
                data.detail ||
                "Offline Piper TTS failed."
            );
        }

        let duration =
            0;

        if (
            Number(data.duration_ms) >
            0
        ) {

            duration =
                Number(
                    data.duration_ms
                ) + 600;

        } else if (
            Number(data.duration) >
            0
        ) {

            duration =
                Number(
                    data.duration
                ) * 1000 + 600;

        } else {

            duration =
                Math.max(
                    2200,
                    Math.min(
                        30000,
                        speechText.length * 72
                    )
                );
        }

        await sleep(
            duration
        );

        if (
            thisTTSId !==
            currentTTSId
        ) {
            return;
        }

    } catch (error) {

        if (
            thisTTSId ===
            currentTTSId
        ) {

            console.error(
                "[JARVIS OFFLINE TTS ERROR]",
                error
            );

            safeSetText(
                activityText,
                "Offline voice output failed."
            );

        }

    } finally {

        if (
            thisTTSId !==
            currentTTSId
        ) {
            return;
        }

        isSpeaking =
            false;

        ttsRequestInProgress =
            false;

        if (
            alwaysListening
        ) {

            setSystemState(
                "listening",
                "offline microphone..."
            );

            safeSetText(
                activityText,
                "Always listening..."
            );

        } else {

            setSystemState(
                "idle",
                "idle"
            );

            safeSetText(
                activityText,
                "Waiting for command..."
            );
        }

        resumeAlwaysOnMicrophone();
    }
}

/* ============================================================
   BACKEND CHAT
============================================================ */

async function requestJarvis(
    formData,
    signal
) {
    const response =
        await fetch(
            CHAT_ENDPOINT,
            {
                method: "POST",
                body: formData,
                signal,
                cache: "no-store"
            }
        );

    const rawText =
        await response.text();

    let data;

    try {

        data =
            JSON.parse(
                rawText
            );

    } catch (_) {

        throw new Error(
            "Backend returned invalid JSON: " +
            rawText.slice(
                0,
                300
            )
        );
    }

    if (!response.ok) {

        throw new Error(
            data.error ||
            data.detail ||
            data.message ||
            `Server error: ${response.status}`
        );
    }

    if (
        data.success === false
    ) {

        throw new Error(
            data.error ||
            data.detail ||
            data.message ||
            "Request failed."
        );
    }

    return String(
        data.reply ??
        data.response ??
        data.answer ??
        data.message ??
        data.text ??
        ""
    );
}

/* ============================================================
   BRAIN COMMAND DETECTOR

   Only VISUAL / 3D commands go directly to jarvisThink().
   Normal conversation MUST stay on /api/chat.
============================================================ */

function isBrainVisualCommand(
    command
) {

    const text =
        normalizeText(
            command
        ).toLowerCase();

    const keywords = [

        "hologram",

        "3d",

        "dna",

        "dna model",

        "dna hologram",

        "particle space",

        "create cube",

        "make cube",

        "create sphere",

        "make sphere",

        "create model",

        "make model",

        "load model",

        "clear hologram",

        "clear 3d",

        "open hologram",

        "open particle",

        "show hologram",

        "show 3d",

        "draw 3d"
    ];

    return keywords.some(
        key =>
            text.includes(key)
    );
}

/* ============================================================
   EXTRACT BRAIN RESULT
============================================================ */

function extractBrainReply(
    result
) {

    if (
        result === null ||
        result === undefined
    ) {
        return "";
    }

    if (
        typeof result ===
        "string"
    ) {
        return result.trim();
    }

    if (
        typeof result ===
        "object"
    ) {

        const possible =
            [

                result.reply,

                result.response,

                result.answer,

                result.message,

                result.text,

                result.result,

                result.status
            ];

        for (
            const value
            of possible
        ) {

            if (
                typeof value ===
                "string" &&
                value.trim()
            ) {

                return value.trim();
            }
        }

        if (
            result.success ===
            true
        ) {
            return "Success";
        }
    }

    return "";
}

/* ============================================================
   SINGLE SEND COMMAND
============================================================ */

async function sendCommand() {

    if (
        isProcessing
    ) {
        return;
    }

    if (
        !userInput
    ) {
        return;
    }

    const typedCommand =
        normalizeText(
            userInput.value
        );

    if (
        !typedCommand &&
        !selectedAttachment
    ) {
        return;
    }

    let commandToSend =
        typedCommand;

    let confirmedFlag =
        false;

    /* ========================================================
       CONFIRMATION
    ======================================================== */

    if (
        pendingConfirmationCommand
    ) {

        if (
            looksLikeConfirmReply(
                typedCommand
            )
        ) {

            commandToSend =
                pendingConfirmationCommand;

            confirmedFlag =
                true;

            pendingConfirmationCommand =
                null;

        } else if (
            looksLikeDenyReply(
                typedCommand
            )
        ) {

            pendingConfirmationCommand =
                null;

            userInput.value =
                "";

            userInput.style.height =
                "auto";

            addChatMessage(
                "user",
                typedCommand
            );

            addChatMessage(
                "jarvis",
                "Cancelled."
            );

            await speakJarvis(
                "Cancelled."
            );

            return;

        } else {

            pendingConfirmationCommand =
                null;
        }
    }

    /* ========================================================
       VISUAL / BRAIN ROUTE

       IMPORTANT:
       Don't bypass normal /api/chat for normal conversation.
    ======================================================== */

    if (
        typeof window.jarvisThink ===
            "function" &&
        !selectedAttachment &&
        isBrainVisualCommand(
            commandToSend
        )
    ) {

        const brainCommand =
            commandToSend;

        console.log(
            "================================"
        );

        console.log(
            "INPUT -> JARVIS BRAIN"
        );

        console.log(
            brainCommand
        );

        console.log(
            "================================"
        );

        pauseAlwaysOnMicrophone();

        isProcessing =
            true;

        if (sendButton) {
            sendButton.disabled =
                true;
        }

        if (stopButton) {
            stopButton.disabled =
                false;
        }

        userInput.value =
            "";

        userInput.style.height =
            "auto";

        addChatMessage(
            "user",
            brainCommand
        );

        const brainWorkerId =
            "coordinator";

        const brainWorker =
            WORKERS[
                brainWorkerId
            ];

        const brainAgent =
            agents[
                brainWorkerId
            ];

        if (brainAgent) {

            brainAgent.state =
                "working";

            brainAgent.targetX =
                CORE_POS.x - 16;

            brainAgent.targetY =
                CORE_POS.y + 40;

            setAgentStatusLabel(
                brainWorkerId,
                "WORKING"
            );
        }

        setSystemState(
            "thinking",
            "JARVIS brain processing..."
        );

        safeSetText(
            activityText,
            "JARVIS Brain is processing..."
        );

        const typing =
            addTypingMessage();

        try {

            const result =
                await Promise.resolve(
                    window.jarvisThink(
                        brainCommand
                    )
                );

            console.log(
                "JARVIS BRAIN RESULT:",
                result
            );

            removeTypingMessage(
                typing
            );

            if (brainAgent) {

                brainAgent.targetX =
                    brainAgent.homeX;

                brainAgent.targetY =
                    brainAgent.homeY;

                brainAgent.state =
                    "completed";

                brainAgent.completedTimer =
                    1500;

                setAgentStatusLabel(
                    brainWorkerId,
                    "DONE"
                );
            }

            let brainReply =
                extractBrainReply(
                    result
                );

            /*
             * Brain/action-router may perform the action successfully
             * and return undefined. Still show + speak success.
             */

            if (!brainReply) {

                brainReply =
                    "Success";
            }

            const visibleReply =
                simplifyToolAnswer(
                    brainReply
                );

            safeSetText(
                activityText,
                "Task completed successfully."
            );

            addChatMessage(
                "jarvis",
                visibleReply
            );

            /*
             * CRITICAL:
             * Brain commands also speak through Piper.
             */

            await speakJarvis(
                brainReply
            );

        } catch (error) {

            console.error(
                "[JARVIS BRAIN ERROR]",
                error
            );

            removeTypingMessage(
                typing
            );

            if (brainAgent) {

                brainAgent.targetX =
                    brainAgent.homeX;

                brainAgent.targetY =
                    brainAgent.homeY;

                brainAgent.state =
                    "error";

                brainAgent.completedTimer =
                    2000;

                setAgentStatusLabel(
                    brainWorkerId,
                    "ERROR"
                );
            }

            const errorText =
                error instanceof Error
                    ? error.message
                    : String(error);

            addChatMessage(
                "jarvis",
                `Sorry. ${errorText}`
            );

            await speakJarvis(
                `Sorry. ${errorText}`
            );

        } finally {

            isProcessing =
                false;

            currentAbortController =
                null;

            if (sendButton) {
                sendButton.disabled =
                    false;
            }

            if (stopButton) {
                stopButton.disabled =
                    true;
            }

            resumeAlwaysOnMicrophone();
        }

        return;
    }

    /* ========================================================
       NORMAL / BACKEND ROUTE
    ======================================================== */

    pauseAlwaysOnMicrophone();

    if (
        isSpeaking ||
        ttsRequestInProgress
    ) {

        await stopJarvisVoice();
    }

    isProcessing =
        true;

    if (sendButton) {
        sendButton.disabled =
            true;
    }

    if (stopButton) {
        stopButton.disabled =
            false;
    }

    /* ========================================================
       USER MESSAGE
    ======================================================== */

    let displayMessage =
        typedCommand;

    if (
        selectedAttachment
    ) {

        const attachmentText =
            `Attachment: ${selectedAttachment.name}`;

        displayMessage =
            typedCommand
                ? `${typedCommand}\n\n${attachmentText}`
                : attachmentText;
    }

    addChatMessage(
        "user",
        displayMessage
    );

    /* ========================================================
       WORKER
    ======================================================== */

    const workerId =
        detectWorker(
            commandToSend,
            selectedAttachment
        );

    const worker =
        WORKERS[
            workerId
        ] ||
        WORKERS.research;

    const agent =
        agents[
            workerId
        ] ||
        agents.research;

    setSystemState(
        "thinking",
        `${worker.name} dispatched`
    );

    if (agent) {

        agent.state =
            "working";

        agent.targetX =
            CORE_POS.x - 16;

        agent.targetY =
            CORE_POS.y + 40;

        setAgentStatusLabel(
            workerId,
            "WORKING"
        );
    }

    safeSetText(
        activityText,
        `${worker.name} is processing the request...`
    );

    /* ========================================================
       FORM DATA
    ======================================================== */

    const formData =
        new FormData();

    formData.append(
        "message",
        commandToSend
    );

    formData.append(
        "confirmed",
        confirmedFlag
            ? "true"
            : "false"
    );

    if (
        selectedAttachment
    ) {

        formData.append(
            "attachments",
            selectedAttachment
        );
    }

    userInput.value =
        "";

    userInput.style.height =
        "auto";

    const typingMessage =
        addTypingMessage();

    currentAbortController =
        new AbortController();

    /* ========================================================
       REQUEST
    ======================================================== */

    try {

        const answer =
            await requestJarvis(
                formData,
                currentAbortController.signal
            );

        /* ====================================================
           CONFIRMATION REQUIRED
        ==================================================== */

        if (
            /^CONFIRMATION_NEEDED:/i.test(
                answer
            )
        ) {

            pendingConfirmationCommand =
                commandToSend;

            const question =
                answer
                    .replace(
                        /^CONFIRMATION_NEEDED:\s*/i,
                        ""
                    )
                    .trim() ||
                "Please confirm this action.";

            removeTypingMessage(
                typingMessage
            );

            if (agent) {

                agent.targetX =
                    agent.homeX;

                agent.targetY =
                    agent.homeY;

                agent.state =
                    "idle";
            }

            setAgentStatusLabel(
                workerId,
                "WAITING"
            );

            safeSetText(
                activityText,
                "Waiting for confirmation..."
            );

            setSystemState(
                "idle",
                "confirmation needed"
            );

            addChatMessage(
                "jarvis",
                question
            );

            await speakJarvis(
                question
            );

            return;
        }

        /* ====================================================
           NORMAL JARVIS RESPONSE
        ==================================================== */

        const finalAnswer =
            simplifyToolAnswer(
                answer
            );

        if (agent) {

            agent.targetX =
                agent.homeX;

            agent.targetY =
                agent.homeY;
        }

        await sleep(
            250
        );

        removeTypingMessage(
            typingMessage
        );

        if (agent) {

            agent.state =
                "completed";

            agent.completedTimer =
                1500;
        }

        setAgentStatusLabel(
            workerId,
            "DONE"
        );

        safeSetText(
            activityText,
            "Task completed successfully."
        );

        /*
         * THIS is the visible JARVIS output.
         */

        addChatMessage(
            "jarvis",
            finalAnswer
        );

        /*
         * THIS is the actual offline voice output.
         */

        await speakJarvis(
            answer
        );

    } catch (error) {

        removeTypingMessage(
            typingMessage
        );

        if (agent) {

            agent.targetX =
                agent.homeX;

            agent.targetY =
                agent.homeY;

            agent.state =
                "error";

            agent.completedTimer =
                2000;
        }

        const aborted =
            error &&
            error.name ===
                "AbortError";

        const errorText =
            aborted
                ? "Task aborted by user."
                : (
                    error instanceof Error
                        ? error.message
                        : String(error)
                );

        if (agent) {

            setAgentStatusLabel(
                workerId,
                aborted
                    ? "STOPPED"
                    : "ERROR"
            );
        }

        safeSetText(
            activityText,
            aborted
                ? "Task aborted."
                : "Task failed."
        );

        setSystemState(
            "idle",
            aborted
                ? "stopped"
                : "error"
        );

        /*
         * Show error.
         */

        addChatMessage(
            "jarvis",
            errorText
        );

        /*
         * Speak error too.
         */

        await speakJarvis(
            aborted
                ? "Task aborted."
                : `Sorry. ${errorText}`
        );

    } finally {

        if (sendButton) {
            sendButton.disabled =
                false;
        }

        if (stopButton) {
            stopButton.disabled =
                true;
        }

        isProcessing =
            false;

        currentAbortController =
            null;

        removeAttachment();

        resumeAlwaysOnMicrophone();
    }
}

/* ============================================================
   INPUT EVENTS
============================================================ */

if (sendButton) {

    sendButton.addEventListener(
        "click",
        sendCommand
    );
}

if (userInput) {

    userInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendCommand();
            }
        }
    );

    userInput.addEventListener(
        "input",
        () => {

            userInput.style.height =
                "auto";

            userInput.style.height =
                `${userInput.scrollHeight}px`;
        }
    );
}

/* ============================================================
   VOICE TIMER
============================================================ */

function clearVoiceTimers() {

    if (voiceRestartTimer) {

        clearTimeout(
            voiceRestartTimer
        );

        voiceRestartTimer =
            null;
    }

    if (voiceChunkTimer) {

        clearTimeout(
            voiceChunkTimer
        );

        voiceChunkTimer =
            null;
    }
}

/* ============================================================
   MIC TRACKS
============================================================ */

function stopMicrophoneTracks() {

    if (!mediaStream) {
        return;
    }

    try {

        mediaStream
            .getTracks()
            .forEach(
                track => {

                    try {
                        track.stop();
                    } catch (_) {}
                }
            );

    } catch (_) {}

    mediaStream =
        null;
}

/* ============================================================
   MIME TYPE
============================================================ */

function selectRecordingMimeType() {

    if (
        typeof MediaRecorder ===
            "undefined"
    ) {
        return "";
    }

    const candidates = [

        "audio/webm;codecs=opus",

        "audio/webm",

        "audio/ogg;codecs=opus",

        "audio/ogg"
    ];

    for (
        const type
        of candidates
    ) {

        try {

            if (
                MediaRecorder.isTypeSupported(
                    type
                )
            ) {

                return type;
            }

        } catch (_) {}
    }

    return "";
}

/* ============================================================
   PAUSE MIC
============================================================ */

function pauseAlwaysOnMicrophone() {

    clearVoiceTimers();

    discardCurrentRecording =
        true;

    if (
        mediaRecorder &&
        isRecordingVoice
    ) {

        try {
            mediaRecorder.stop();
        } catch (_) {}
    }

    stopMicrophoneTracks();

    mediaRecorder =
        null;

    isRecordingVoice =
        false;

    microphoneBusy =
        false;

    if (micButton) {

        micButton.classList.remove(
            "listening"
        );
    }
}

/* ============================================================
   RESUME MIC
============================================================ */

function resumeAlwaysOnMicrophone() {

    if (
        !alwaysListening
    ) {
        return;
    }

    if (
        isProcessing ||
        isSpeaking ||
        ttsRequestInProgress ||
        isRecordingVoice ||
        microphoneBusy
    ) {
        return;
    }

    scheduleVoiceRestart();
}

/* ============================================================
   MIC RESTART
============================================================ */

function scheduleVoiceRestart() {

    if (
        !alwaysListening
    ) {
        return;
    }

    if (
        isProcessing ||
        isSpeaking ||
        ttsRequestInProgress ||
        isRecordingVoice ||
        microphoneBusy
    ) {
        return;
    }

    if (voiceRestartTimer) {

        clearTimeout(
            voiceRestartTimer
        );
    }

    voiceRestartTimer =
        setTimeout(
            () => {

                voiceRestartTimer =
                    null;

                if (
                    alwaysListening &&
                    !isProcessing &&
                    !isSpeaking &&
                    !ttsRequestInProgress &&
                    !isRecordingVoice &&
                    !microphoneBusy
                ) {

                    beginAlwaysOnRecording();
                }

            },
            500
        );
}

/* ============================================================
   START ALWAYS-ON RECORDING
============================================================ */

async function beginAlwaysOnRecording() {

    if (
        !alwaysListening ||
        isProcessing ||
        isSpeaking ||
        ttsRequestInProgress ||
        isRecordingVoice ||
        microphoneBusy
    ) {
        return;
    }

    if (
        !navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia
    ) {

        safeSetText(
            activityText,
            "Microphone API unavailable."
        );

        setSystemState(
            "idle",
            "microphone unavailable"
        );

        return;
    }

    if (
        typeof MediaRecorder ===
            "undefined"
    ) {

        safeSetText(
            activityText,
            "MediaRecorder unavailable."
        );

        setSystemState(
            "idle",
            "audio recording unavailable"
        );

        return;
    }

    microphoneBusy =
        true;

    try {

        mediaStream =
            await navigator.mediaDevices.getUserMedia(
                {
                    audio: {

                        channelCount:
                            1,

                        echoCancellation:
                            true,

                        noiseSuppression:
                            true,

                        autoGainControl:
                            true
                    }
                }
            );

        recordedChunks =
            [];

        discardCurrentRecording =
            false;

        const mimeType =
            selectRecordingMimeType();

        mediaRecorder =
            mimeType
                ? new MediaRecorder(
                    mediaStream,
                    {
                        mimeType
                    }
                )
                : new MediaRecorder(
                    mediaStream
                );

        /* ====================================================
           DATA
        ==================================================== */

        mediaRecorder.ondataavailable =
            event => {

                if (
                    event.data &&
                    event.data.size > 0
                ) {

                    recordedChunks.push(
                        event.data
                    );
                }
            };

        /* ====================================================
           ERROR
        ==================================================== */

        mediaRecorder.onerror =
            event => {

                console.error(
                    "[JARVIS MIC ERROR]",
                    event.error
                );
            };

        /* ====================================================
           STOP
        ==================================================== */

        mediaRecorder.onstop =
            async () => {

                const shouldDiscard =
                    discardCurrentRecording;

                const chunks =
                    recordedChunks.slice();

                recordedChunks =
                    [];

                isRecordingVoice =
                    false;

                mediaRecorder =
                    null;

                stopMicrophoneTracks();

                if (micButton) {

                    micButton.classList.remove(
                        "listening"
                    );
                }

                /* =========================================
                   DISCARD CURRENT RECORDING
                ========================================= */

                if (
                    shouldDiscard
                ) {

                    microphoneBusy =
                        false;

                    resumeAlwaysOnMicrophone();

                    return;
                }

                /* =========================================
                   DISABLED
                ========================================= */

                if (
                    !alwaysListening
                ) {

                    microphoneBusy =
                        false;

                    return;
                }

                /* =========================================
                   JARVIS BUSY
                ========================================= */

                if (
                    isProcessing ||
                    isSpeaking ||
                    ttsRequestInProgress
                ) {

                    microphoneBusy =
                        false;

                    resumeAlwaysOnMicrophone();

                    return;
                }

                try {

                    const audioType =
                        mimeType ||
                        "audio/webm";

                    const blob =
                        new Blob(
                            chunks,
                            {
                                type:
                                    audioType
                            }
                        );

                    if (
                        blob.size >
                        0
                    ) {

                        safeSetText(
                            activityText,
                            "Transcribing offline..."
                        );

                        setSystemState(
                            "thinking",
                            "local Whisper..."
                        );

                        await transcribeOfflineAudio(
                            blob
                        );
                    }

                } catch (error) {

                    console.error(
                        "[JARVIS STT ERROR]",
                        error
                    );

                    safeSetText(
                        activityText,
                        "Offline transcription failed."
                    );

                    setSystemState(
                        "idle",
                        "STT error"
                    );

                } finally {

                    microphoneBusy =
                        false;

                    resumeAlwaysOnMicrophone();
                }
            };

        /* ====================================================
           START
        ==================================================== */

        mediaRecorder.start();

        isRecordingVoice =
            true;

        microphoneBusy =
            false;

        if (micButton) {

            micButton.classList.add(
                "listening"
            );
        }

        safeSetText(
            activityText,
            "Always listening..."
        );

        setSystemState(
            "listening",
            "offline microphone..."
        );

        voiceChunkTimer =
            setTimeout(
                () => {

                    if (
                        mediaRecorder &&
                        isRecordingVoice
                    ) {

                        try {
                            mediaRecorder.stop();
                        } catch (_) {}
                    }

                },
                VOICE_CHUNK_SECONDS *
                    1000
            );

    } catch (error) {

        console.error(
            "[JARVIS MIC ERROR]",
            error
        );

        microphoneBusy =
            false;

        isRecordingVoice =
            false;

        mediaRecorder =
            null;

        stopMicrophoneTracks();

        if (micButton) {

            micButton.classList.remove(
                "listening"
            );
        }

        const errorName =
            error &&
            error.name
                ? error.name
                : "";

        if (
            errorName ===
                "NotAllowedError" ||
            errorName ===
                "PermissionDeniedError"
        ) {

            alwaysListening =
                false;

            safeSetText(
                activityText,
                "Microphone permission denied."
            );

            setSystemState(
                "idle",
                "microphone denied"
            );

            return;
        }

        safeSetText(
            activityText,
            "Microphone unavailable."
        );

        setSystemState(
            "idle",
            "microphone error"
        );

        scheduleVoiceRestart();
    }
}

/* ============================================================
   OFFLINE STT
============================================================ */

async function transcribeOfflineAudio(
    blob
) {

    if (
        !blob ||
        blob.size === 0
    ) {
        return;
    }

    const formData =
        new FormData();

    let filename =
        "jarvis_voice.webm";

    if (
        blob.type &&
        blob.type.includes("ogg")
    ) {

        filename =
            "jarvis_voice.ogg";
    }

    formData.append(
        "file",
        blob,
        filename
    );

    const response =
        await fetch(
            TRANSCRIBE_ENDPOINT,
            {
                method: "POST",
                body: formData,
                cache: "no-store"
            }
        );

    const rawText =
        await response.text();

    let data;

    try {

        data =
            JSON.parse(
                rawText
            );

    } catch (_) {

        throw new Error(
            "Transcription server returned invalid JSON."
        );
    }

    if (
        !response.ok ||
        data.success === false
    ) {

        throw new Error(
            data.error ||
            data.detail ||
            "Offline transcription failed."
        );
    }

    const transcript =
        normalizeText(
            data.text ||
            ""
        );

    if (!transcript) {

        safeSetText(
            activityText,
            "Always listening..."
        );

        setSystemState(
            "listening",
            "waiting for voice..."
        );

        return;
    }

    console.log(
        "[JARVIS OFFLINE STT]",
        transcript
    );

    if (
        isProcessing ||
        isSpeaking ||
        ttsRequestInProgress
    ) {
        return;
    }

    if (userInput) {

        userInput.value =
            transcript;

        userInput.dispatchEvent(
            new Event(
                "input"
            )
        );
    }

    safeSetText(
        activityText,
        "Voice command received."
    );

    setTimeout(
        () => {

            if (
                !isProcessing &&
                !isSpeaking &&
                !ttsRequestInProgress &&
                userInput &&
                normalizeText(
                    userInput.value
                )
            ) {

                sendCommand();
            }

        },
        100
    );
}

/* ============================================================
   MIC TOGGLE
============================================================ */

function toggleAlwaysListening() {

    alwaysListening =
        !alwaysListening;

    if (
        !alwaysListening
    ) {

        clearVoiceTimers();

        discardCurrentRecording =
            true;

        if (
            mediaRecorder &&
            isRecordingVoice
        ) {

            try {
                mediaRecorder.stop();
            } catch (_) {}
        }

        stopMicrophoneTracks();

        mediaRecorder =
            null;

        isRecordingVoice =
            false;

        microphoneBusy =
            false;

        if (micButton) {

            micButton.classList.remove(
                "listening"
            );
        }

        safeSetText(
            activityText,
            "Always-on microphone disabled."
        );

        setSystemState(
            "idle",
            "microphone off"
        );

        return;
    }

    if (micButton) {

        micButton.classList.add(
            "listening"
        );
    }

    safeSetText(
        activityText,
        "Always-on microphone enabled."
    );

    resumeAlwaysOnMicrophone();
}

if (micButton) {

    micButton.addEventListener(
        "click",
        toggleAlwaysListening
    );
}

/* ============================================================
   STOP BUTTON
============================================================ */

if (stopButton) {

    stopButton.addEventListener(
        "click",
        async () => {

            if (
                currentAbortController
            ) {

                try {

                    currentAbortController.abort();

                } catch (_) {}
            }

            pauseAlwaysOnMicrophone();

            await stopJarvisVoice();

            Object.values(
                agents
            ).forEach(
                agent => {

                    if (
                        agent.state ===
                        "working"
                    ) {

                        agent.targetX =
                            agent.homeX;

                        agent.targetY =
                            agent.homeY;

                        agent.state =
                            "idle";

                        setAgentStatusLabel(
                            agent.id,
                            "STOPPED"
                        );
                    }
                }
            );

            safeSetText(
                activityText,
                "Stopped."
            );

            setSystemState(
                "idle",
                "stopped"
            );

            resumeAlwaysOnMicrophone();
        }
    );
}

/* ============================================================
   GESTURE CONTROL
   EXTERNAL ENGINE UNTOUCHED
============================================================ */

function startJarvisGesture() {

    try {

        if (
            typeof JarvisHandTracker !==
                "undefined" &&
            JarvisHandTracker.start
        ) {

            JarvisHandTracker.start();
        }

    } catch (error) {

        console.error(
            "[GESTURE START ERROR]",
            error
        );
    }

    gestureActive =
        true;

    safeSetText(
        activityText,
        "Gesture Control Active"
    );

    setSystemState(
        "listening",
        "hand gesture mode"
    );
}

function stopJarvisGesture() {

    try {

        if (
            typeof JarvisHandTracker !==
                "undefined" &&
            JarvisHandTracker.stop
        ) {

            JarvisHandTracker.stop();
        }

    } catch (error) {

        console.error(
            "[GESTURE STOP ERROR]",
            error
        );
    }

    gestureActive =
        false;

    safeSetText(
        activityText,
        "Gesture Control Disabled"
    );

    setSystemState(
        alwaysListening
            ? "listening"
            : "idle",
        alwaysListening
            ? "offline microphone..."
            : "idle"
    );
}

if (gestureButton) {

    gestureButton.addEventListener(
        "click",
        () => {

            if (
                gestureActive
            ) {

                stopJarvisGesture();

            } else {

                startJarvisGesture();
            }
        }
    );
}

/* ============================================================
   PIXEL OFFICE
============================================================ */

const PALETTE = {

    h: "#2b2035",

    f: "#e8b48a",

    p: "#101822",

    s: "#05080d"
};

const SPRITE_FRONT = [

    "................",

    ".....hhhhhh.....",

    "....hhhhhhhh....",

    "....hffffffh....",

    "....hffffffh....",

    "....hffffffh....",

    ".....ffffff.....",

    "....bbbbbbbb....",

    "...bbbbbbbbbb...",

    "...bbbbbbbbbb...",

    "...bbbbbbbbbb...",

    "...bb......bb...",

    "...bb......bb...",

    "....pp....pp....",

    "....pp....pp....",

    "....pp....pp....",

    "....pp....pp....",

    "....ss....ss....",

    "................"
];

const SPRITE_BACK = [

    "................",

    ".....hhhhhh.....",

    "....hhhhhhhh....",

    "....hhhhhhhh....",

    "....hhhhhhhh....",

    "....hhhhhhhh....",

    ".....hhhhhh.....",

    "....bbbbbbbb....",

    "...bbbbbbbbbb...",

    "...bbbbbbbbbb...",

    "...bbbbbbbbbb...",

    "...bb......bb...",

    "...bb......bb...",

    "....pp....pp....",

    "....pp....pp....",

    "....pp....pp....",

    "....pp....pp....",

    "....ss....ss....",

    "................"
];

const WALK_FRAMES = [
    0,
    -1,
    0,
    1
];

const CORE_POS = {
    x: 480,
    y: 130
};

const DESK_LAYOUT = [

    {
        id: "coordinator",
        x: 120,
        y: 360
    },

    {
        id: "research",
        x: 300,
        y: 390
    },

    {
        id: "vision",
        x: 480,
        y: 400
    },

    {
        id: "image",
        x: 660,
        y: 390
    },

    {
        id: "tool",
        x: 840,
        y: 360
    }
];

/* ============================================================
   SPRITE DRAW
============================================================ */

function drawSprite(
    ctx,
    rows,
    roleColor,
    x,
    y,
    scale,
    flip,
    legOffset
) {

    if (!ctx) {
        return;
    }

    ctx.save();

    ctx.translate(
        x,
        y
    );

    if (flip) {

        ctx.scale(
            -1,
            1
        );

        ctx.translate(
            -rows[0].length *
                scale,
            0
        );
    }

    for (
        let r = 0;
        r < rows.length;
        r++
    ) {

        const row =
            rows[r];

        for (
            let c = 0;
            c < row.length;
            c++
        ) {

            const ch =
                row[c];

            if (
                ch === "."
            ) {
                continue;
            }

            const color =
                ch === "b"
                    ? roleColor
                    : (
                        PALETTE[ch] ||
                        "#ffffff"
                    );

            let columnOffset =
                0;

            if (
                r >= 13 &&
                r <= 17
            ) {

                columnOffset =
                    legOffset;
            }

            ctx.fillStyle =
                color;

            ctx.fillRect(
                (
                    c +
                    columnOffset
                ) * scale,

                r * scale,

                scale,

                scale
            );
        }
    }

    ctx.restore();
}

/* ============================================================
   AGENTS
============================================================ */

const agents = {};

DESK_LAYOUT.forEach(
    desk => {

        agents[
            desk.id
        ] = {

            id:
                desk.id,

            homeX:
                desk.x,

            homeY:
                desk.y,

            x:
                desk.x,

            y:
                desk.y,

            targetX:
                desk.x,

            targetY:
                desk.y,

            dir:
                "front",

            flip:
                false,

            walking:
                false,

            frame:
                0,

            frameTimer:
                0,

            completedTimer:
                0,

            state:
                "idle"
        };
    }
);

/* ============================================================
   TAGS
============================================================ */

const tagEls = {};

if (tagLayer) {

    DESK_LAYOUT.forEach(
        desk => {

            const element =
                document.createElement(
                    "div"
                );

            element.className =
                `agent-tag role-${desk.id}`;

            element.innerHTML = `
                <span class="name-line">
                    ${WORKERS[desk.id].name}
                </span>

                <span class="status-line">
                    IDLE
                </span>
            `;

            tagLayer.appendChild(
                element
            );

            tagEls[
                desk.id
            ] =
                element;
        }
    );
}

function setAgentStatusLabel(
    id,
    text
) {

    const element =
        tagEls[id];

    if (!element) {
        return;
    }

    const status =
        element.querySelector(
            ".status-line"
        );

    if (status) {

        status.textContent =
            text;
    }
}

function updateTagPositions() {

    if (
        !officeCanvas
    ) {
        return;
    }

    const scaleX =
        officeCanvas.clientWidth /
        officeCanvas.width;

    const scaleY =
        officeCanvas.clientHeight /
        officeCanvas.height;

    Object.values(
        agents
    ).forEach(
        agent => {

            const element =
                tagEls[
                    agent.id
                ];

            if (!element) {
                return;
            }

            element.style.left =
                `${
                    agent.x *
                        scaleX +
                    16 *
                        scaleX
                }px`;

            element.style.top =
                `${
                    agent.y *
                        scaleY -
                    6 *
                        scaleY
                }px`;
        }
    );
}

/* ============================================================
   BACKGROUND
============================================================ */

const bgCanvas =
    document.createElement(
        "canvas"
    );

if (officeCanvas) {

    bgCanvas.width =
        officeCanvas.width;

    bgCanvas.height =
        officeCanvas.height;
}

const bgCtx =
    bgCanvas.getContext(
        "2d"
    );

bgCtx.imageSmoothingEnabled =
    false;

function drawFloor() {

    if (!officeCanvas) {
        return;
    }

    const width =
        bgCanvas.width;

    const height =
        bgCanvas.height;

    bgCtx.clearRect(
        0,
        0,
        width,
        height
    );

    bgCtx.fillStyle =
        "#0d1620";

    bgCtx.fillRect(
        0,
        0,
        width,
        height
    );

    bgCtx.strokeStyle =
        "rgba(255,255,255,0.035)";

    bgCtx.lineWidth =
        1;

    for (
        let x = 0;
        x <= width;
        x += 32
    ) {

        bgCtx.beginPath();

        bgCtx.moveTo(
            x,
            0
        );

        bgCtx.lineTo(
            x,
            height
        );

        bgCtx.stroke();
    }

    for (
        let y = 0;
        y <= height;
        y += 32
    ) {

        bgCtx.beginPath();

        bgCtx.moveTo(
            0,
            y
        );

        bgCtx.lineTo(
            width,
            y
        );

        bgCtx.stroke();
    }

    const wallGradient =
        bgCtx.createLinearGradient(
            0,
            0,
            0,
            90
        );

    wallGradient.addColorStop(
        0,
        "#131f2c"
    );

    wallGradient.addColorStop(
        1,
        "rgba(19,31,44,0)"
    );

    bgCtx.fillStyle =
        wallGradient;

    bgCtx.fillRect(
        0,
        0,
        width,
        90
    );

    bgCtx.strokeStyle =
        "rgba(79,215,255,0.25)";

    bgCtx.fillStyle =
        "rgba(79,215,255,0.08)";

    bgCtx.fillRect(
        width / 2 - 100,
        18,
        200,
        55
    );

    bgCtx.strokeRect(
        width / 2 - 100,
        18,
        200,
        55
    );

    bgCtx.beginPath();

    bgCtx.moveTo(
        width / 2,
        18
    );

    bgCtx.lineTo(
        width / 2,
        73
    );

    bgCtx.stroke();

    DESK_LAYOUT.forEach(
        desk => {

            const dx =
                desk.x - 24;

            const dy =
                desk.y + 20;

            bgCtx.fillStyle =
                "#1b2733";

            bgCtx.fillRect(
                dx,
                dy,
                96,
                14
            );

            bgCtx.fillStyle =
                "#111a24";

            bgCtx.fillRect(
                dx,
                dy + 14,
                96,
                6
            );

            bgCtx.fillStyle =
                "#0b1520";

            bgCtx.fillRect(
                dx + 34,
                dy - 30,
                28,
                22
            );

            bgCtx.fillStyle =
                ROLE_COLORS[
                    desk.id
                ];

            bgCtx.globalAlpha =
                0.5;

            bgCtx.fillRect(
                dx + 37,
                dy - 27,
                22,
                4
            );

            bgCtx.fillRect(
                dx + 37,
                dy - 20,
                14,
                4
            );

            bgCtx.globalAlpha =
                1;
        }
    );

    bgCtx.save();

    bgCtx.translate(
        CORE_POS.x,
        CORE_POS.y
    );

    const coreGradient =
        bgCtx.createRadialGradient(
            0,
            10,
            4,
            0,
            10,
            70
        );

    coreGradient.addColorStop(
        0,
        "rgba(79,215,255,0.35)"
    );

    coreGradient.addColorStop(
        1,
        "rgba(79,215,255,0)"
    );

    bgCtx.fillStyle =
        coreGradient;

    bgCtx.fillRect(
        -90,
        -60,
        180,
        140
    );

    bgCtx.fillStyle =
        "#0b1520";

    bgCtx.fillRect(
        -22,
        -10,
        44,
        52
    );

    bgCtx.strokeStyle =
        "rgba(79,215,255,0.6)";

    bgCtx.strokeRect(
        -22,
        -10,
        44,
        52
    );

    bgCtx.fillStyle =
        "#4fd7ff";

    bgCtx.font =
        "12px sans-serif";

    bgCtx.textAlign =
        "center";

    bgCtx.fillText(
        "J",
        0,
        22
    );

    bgCtx.restore();
}

drawFloor();

/* ============================================================
   OFFICE LOOP
============================================================ */

let lastTs = 0;

function officeLoop(
    timestamp
) {

    if (
        !officeCanvas ||
        !octx
    ) {

        requestAnimationFrame(
            officeLoop
        );

        return;
    }

    const dt =
        Math.min(
            timestamp -
                lastTs ||
                16,
            48
        );

    lastTs =
        timestamp;

    Object.values(
        agents
    ).forEach(
        agent => {

            const dx =
                agent.targetX -
                agent.x;

            const dy =
                agent.targetY -
                agent.y;

            const distance =
                Math.hypot(
                    dx,
                    dy
                );

            if (
                distance > 2
            ) {

                agent.walking =
                    true;

                const speed =
                    0.16 *
                    dt;

                agent.x +=
                    (
                        dx /
                        distance
                    ) *
                    Math.min(
                        speed,
                        distance
                    );

                agent.y +=
                    (
                        dy /
                        distance
                    ) *
                    Math.min(
                        speed,
                        distance
                    );

                agent.dir =
                    dy < -0.2
                        ? "back"
                        : "front";

                agent.flip =
                    dx < -0.2
                        ? true
                        : dx > 0.2
                            ? false
                            : agent.flip;

                agent.frameTimer +=
                    dt;

                if (
                    agent.frameTimer >
                    110
                ) {

                    agent.frame =
                        (
                            agent.frame +
                            1
                        ) %
                        WALK_FRAMES.length;

                    agent.frameTimer =
                        0;
                }

            } else {

                agent.walking =
                    false;

                agent.frame =
                    0;
            }

            if (
                agent.state ===
                    "completed" ||
                agent.state ===
                    "error"
            ) {

                agent.completedTimer -=
                    dt;

                if (
                    agent.completedTimer <=
                    0
                ) {

                    agent.state =
                        "idle";

                    setAgentStatusLabel(
                        agent.id,
                        "IDLE"
                    );
                }
            }
        }
    );

    octx.clearRect(
        0,
        0,
        officeCanvas.width,
        officeCanvas.height
    );

    octx.drawImage(
        bgCanvas,
        0,
        0
    );

    const sorted =
        Object.values(
            agents
        ).sort(
            (a, b) =>
                a.y - b.y
        );

    sorted.forEach(
        agent => {

            const rows =
                agent.dir ===
                    "back"
                    ? SPRITE_BACK
                    : SPRITE_FRONT;

            const legOffset =
                agent.walking
                    ? WALK_FRAMES[
                        agent.frame
                    ]
                    : 0;

            const scale =
                3;

            const bob =
                agent.state ===
                    "working" &&
                !agent.walking
                    ? Math.sin(
                        timestamp /
                            180
                    ) * 2
                    : 0;

            if (
                agent.state ===
                    "working" ||
                agent.state ===
                    "completed" ||
                agent.state ===
                    "error"
            ) {

                octx.save();

                octx.globalAlpha =
                    0.5;

                octx.strokeStyle =
                    agent.state ===
                        "error"
                        ? "#ff6b7a"
                        : agent.state ===
                            "completed"
                            ? "#57e6a4"
                            : ROLE_COLORS[
                                agent.id
                            ];

                octx.lineWidth =
                    2;

                octx.beginPath();

                octx.ellipse(
                    agent.x +
                        (
                            16 *
                            scale /
                            2
                        ),

                    agent.y +
                        18 *
                        scale -
                        2,

                    26,

                    8,

                    0,

                    0,

                    Math.PI *
                        2
                );

                octx.stroke();

                octx.restore();
            }

            drawSprite(
                octx,
                rows,
                ROLE_COLORS[
                    agent.id
                ],
                agent.x,
                agent.y + bob,
                scale,
                agent.flip,
                legOffset
            );
        }
    );

    updateTagPositions();

    requestAnimationFrame(
        officeLoop
    );
}

if (
    officeCanvas &&
    octx
) {

    requestAnimationFrame(
        officeLoop
    );
}

/* ============================================================
   ORB
============================================================ */

function orbLoop(
    timestamp
) {

    if (
        !orbCanvas ||
        !octx2
    ) {

        requestAnimationFrame(
            orbLoop
        );

        return;
    }

    const width =
        orbCanvas.width;

    const height =
        orbCanvas.height;

    const cx =
        width / 2;

    const cy =
        height / 2;

    octx2.clearRect(
        0,
        0,
        width,
        height
    );

    const active =
        systemState ===
            "thinking" ||

        systemState ===
            "speaking" ||

        systemState ===
            "listening";

    const coreR =
        active
            ? 16 +
                Math.sin(
                    timestamp /
                        160
                ) *
                2
            : 13;

    [
        [
            46,
            0.35,
            timestamp /
                2600,
            false
        ],

        [
            36,
            0.5,
            -timestamp /
                1800,
            true
        ]
    ].forEach(
        (
            [
                radius,
                alpha,
                rotation,
                dashed
            ]
        ) => {

            octx2.save();

            octx2.translate(
                cx,
                cy
            );

            octx2.rotate(
                rotation
            );

            octx2.strokeStyle =
                `rgba(79,215,255,${
                    active
                        ? alpha
                        : alpha *
                            0.4
                })`;

            octx2.lineWidth =
                1;

            octx2.setLineDash(
                dashed
                    ? [4, 4]
                    : []
            );

            octx2.beginPath();

            octx2.arc(
                0,
                0,
                radius,
                0,
                Math.PI *
                    2
            );

            octx2.stroke();

            octx2.restore();
        }
    );

    if (active) {

        for (
            let i = 0;
            i < 6;
            i++
        ) {

            const angle =
                timestamp /
                    500 +
                i *
                    (
                        Math.PI *
                        2 /
                        6
                    );

            const radius =
                40;

            const px =
                cx +
                Math.cos(
                    angle
                ) *
                radius;

            const py =
                cy +
                Math.sin(
                    angle
                ) *
                radius *
                0.55;

            octx2.fillStyle =
                "rgba(147,199,255,0.85)";

            octx2.beginPath();

            octx2.arc(
                px,
                py,
                1.6,
                0,
                Math.PI *
                    2
            );

            octx2.fill();
        }
    }

    const gradient =
        octx2.createRadialGradient(
            cx - 4,
            cy - 6,
            2,
            cx,
            cy,
            coreR
        );

    gradient.addColorStop(
        0,
        active
            ? "#eafcff"
            : "#d5f8ff"
    );

    gradient.addColorStop(
        1,
        active
            ? "#4fd7ff"
            : "#2a8fb0"
    );

    octx2.fillStyle =
        gradient;

    octx2.beginPath();

    octx2.arc(
        cx,
        cy,
        coreR,
        0,
        Math.PI *
            2
    );

    octx2.fill();

    requestAnimationFrame(
        orbLoop
    );
}

if (
    orbCanvas &&
    octx2
) {

    requestAnimationFrame(
        orbLoop
    );
}

/* ============================================================
   RESPONSIVE CANVAS
============================================================ */

function fitCanvas() {

    if (!officeCanvas) {
        return;
    }

    const parent =
        officeCanvas.parentElement;

    if (!parent) {
        return;
    }

    const width =
        parent.clientWidth;

    if (!width) {
        return;
    }

    const aspect =
        officeCanvas.height /
        officeCanvas.width;

    officeCanvas.style.width =
        width + "px";

    officeCanvas.style.height =
        (
            width *
            aspect
        ) + "px";

    updateTagPositions();
}

window.addEventListener(
    "resize",
    fitCanvas
);

fitCanvas();

/* ============================================================
   GLOBAL EXPORTS
============================================================ */

window.sendCommand =
    sendCommand;

window.speakJarvis =
    speakJarvis;

window.stopJarvisVoice =
    stopJarvisVoice;

window.toggleAlwaysListening =
    toggleAlwaysListening;

window.transcribeOfflineAudio =
    transcribeOfflineAudio;

window.startJarvisGesture =
    startJarvisGesture;

window.stopJarvisGesture =
    stopJarvisGesture;

/* ============================================================
   SYSTEM CHECK
============================================================ */

window.jarvisSystemCheck =
function () {

    console.log(
        "============================================"
    );

    console.log(
        "🔥 JARVIS SYSTEM CHECK"
    );

    console.log(
        "Brain:",
        typeof window.jarvisThink
    );

    console.log(
        "Router:",
        typeof window.executeAIAction
    );

    console.log(
        "ThreeD:",
        typeof window.create3DObject
    );

    console.log(
        "Hologram:",
        typeof window.openHologramWorkspace
    );

    console.log(
        "sendCommand:",
        typeof window.sendCommand
    );

    console.log(
        "speakJarvis:",
        typeof window.speakJarvis
    );

    console.log(
        "============================================"
    );
};

/* ============================================================
   STARTUP
============================================================ */

setSystemState(
    "idle"
);

console.log(
    "============================================"
);

console.log(
    "🔥 JARVIS OFFLINE VOICE FRONTEND"
);

console.log(
    "Chat:",
    CHAT_ENDPOINT
);

console.log(
    "Offline STT:",
    TRANSCRIBE_ENDPOINT
);

console.log(
    "Offline TTS:",
    SPEAK_ENDPOINT
);

console.log(
    "MediaRecorder:",
    typeof MediaRecorder !==
        "undefined"
);

console.log(
    "Microphone API:",
    !!(
        navigator.mediaDevices &&
        navigator.mediaDevices.getUserMedia
    )
);

console.log(
    "Browser speechSynthesis: DISABLED"
);

console.log(
    "Browser SpeechRecognition: DISABLED"
);

console.log(
    "Piper TTS: ENABLED"
);

console.log(
    "Anti Echo: ENABLED"
);

console.log(
    "============================================"
);

/* ============================================================
   FINAL LOAD CHECK
============================================================ */

window.addEventListener(
    "load",
    () => {

        console.log(
            "============================================"
        );

        console.log(
            "🔥 JARVIS FINAL SYSTEM CHECK"
        );

        console.log(
            "Brain:",
            typeof window.jarvisThink
        );

        console.log(
            "Router:",
            typeof window.executeAIAction
        );

        console.log(
            "sendCommand:",
            typeof window.sendCommand
        );

        console.log(
            "Piper:",
            typeof window.speakJarvis
        );

        console.log(
            "============================================"
        );

        setTimeout(
            () => {

                if (
                    alwaysListening &&
                    !isProcessing &&
                    !isSpeaking
                ) {

                    beginAlwaysOnRecording();
                }

            },
            800
        );
    }
);