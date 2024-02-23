// Menu

var navLinks = document.getElementById("navLinks")

function showMenu() {
    navLinks.style.right = "0"
}
function hideMenu() {
    navLinks.style.right = "-200px"
}



// Chat

const chatInput = document.querySelector(".chat-input textarea")
const sendChatBtn = document.querySelector(".chat-input span")
const chatbox = document.querySelector(".chatbox")

let userMessage = null;
let assist_id = "asst_Iydh5lFCJn3e2U37sC5iPzDS";
let thread_id = null;
let intent_thread_id = null;
let instructions_bool=true;
let responseMessage;

const createChatLi = (message, className) => {
    const chatLi = document.createElement('li')
    chatLi.classList.add("chat",className);
    let chatContent = className === "outgoing" ? `<p>${message}</p>` : `<span class="material-symbols-outlined">smart_toy</span><p>${message}</p>`
    chatLi.innerHTML = chatContent;
    return chatLi;
}

const generateResponse = (incomingChatLi) => {
    const API_URL = "http://localhost:8000/get_response";
    const messageElement = incomingChatLi.querySelector("p");

    const requestBody = {
        message: userMessage,
        assist_id: assist_id,
        thread_id:thread_id,
        intent_thread_id:intent_thread_id,
        instructions_bool: instructions_bool
    };

    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody)
    };
    

    responseMessage = fetch(API_URL, requestOptions)
    .then(res => {
        if (!res.ok) {
            throw new Error('Network response was not ok');
        }
        return res.json()

    }).then(data => {

        console.log(data)

        if (typeof data.message == 'string') {
            messageElement.textContent = data.message;
            console.log(messageElement.textContent)
        }

        else if (Array.isArray(data.message)) {
            messageElement.textContent = data.message.join('\n');
            console.log(messageElement.textContent)
        }

        else {
            messageElement.textContent = "Oops! Something went wrong. I can not assist you at the moment, consider contacting the human support team! :-)"
            console.log("'else' happend inside fetch of responseMessage.")
            console.log(data.message)
        }
    thread_id = data.thread_id
    intent_thread_id = data.intent_thread_id
    instructions_bool = data.instructions_bool
    console.log(messageElement.textContent)
    }).catch((error) => {
        console.error('Error in catch:', error)
        messageElement.textContent = "Oops! Something went wrong. I can not assist you at the moment, consider contacting the human support team! :-)";
    });
}

const handleChat = () => {
    userMessage = chatInput.value.trim();
    if(!userMessage) return;

    chatbox.appendChild(createChatLi(userMessage, 'outgoing'));

    setTimeout(async () => {
        const incomingChatLi = createChatLi("Thinking...", "incoming")
        chatbox.appendChild(incomingChatLi);
        await generateResponse(incomingChatLi);
    }, 600);
}

sendChatBtn.addEventListener("click", handleChat)