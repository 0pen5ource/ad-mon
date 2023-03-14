import { writable } from 'svelte/store';
import {subscribe} from "svelte/internal";

const messageStore = writable('');

let socket = null;

const sendMessage = (message) => {
    if (socket.readyState <= 1) {
        socket.send(message);
    }
}

const subscribeWs = (callback) => {
    try {
        socket = new WebSocket('ws://127.0.0.1:5000/echo');

// Connection opened
        socket.addEventListener('open', function (event) {
            console.log("It's open");
        });

// Listen for messages
        socket.addEventListener('message', function (event) {
            messageStore.set(event.data);
        });
        messageStore.subscribe(callback);
    } catch (e) {
        debugger
        console.log(e)
    }
}


export default {
    subscribe: subscribeWs,
    sendMessage
}

