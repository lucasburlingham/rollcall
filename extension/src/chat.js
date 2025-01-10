// This script controls the chat functionality of the extension.
// It listens for, sends, and displays messages in the chat window


// Path for getting existing messages from the server
const get_api_url = 'https://127.0.0.1:8080/api/';


window.onload = getMessages;

var submit_button = document.getElementById('submit-button');
submit_button.addEventListener('click', async (event) => {
	event.preventDefault();
	await sendMessage();
});


// Add a message to the chat window
function addMessage(message) {
	// Create a new div element
	var newMessage = document.createElement('div');
	// Add the message to the div
	newMessage.innerHTML = message;
	// Add the div to the chat window
	document.getElementById('chat-window').appendChild(newMessage);
}

// Function to send a message
function sendMessage() {
	// Set the sender_id to a random number between 1 and 1,000,000
	var sender_id = Math.floor(Math.random() * 1000000);

	// Set the api_token to a testing string
	var api_token = "test123testingtesting";

	// Get the message from the input field
	var message = document.getElementById('message-input').value;
	// Clear the input field
	document.getElementById('message-input').value = '';

	// Create a connection to the background script
	let port = browser.runtime.connect({ name: 'send_message' });

	// Send the message to the background script
	port.postMessage({
		message: message,
		sender_id: sender_id,
		api_token: api_token
	});

	// Listen for a response from the background script
	port.onMessage.addListener(response => {
		console.log('chat.js: Response from background script:', response);
	});

	console.log('chat.js: Message sent');
	console.info("Message: " + message);
	console.info("Sender ID: " + sender_id);
	console.info("API Token: " + api_token);
}


async function getSiteName() {
	// get the site name from the current tab
	return new Promise((resolve, reject) => {
		const data = { name: 'get_site_name' };
		console.log('chat.js: Sending message to get site name:');
		console.log(data);
		// Create port to communicate with the background script
		var port = browser.runtime.connect({ name: 'get_site_name' });
		// Get the site name from the background script
		port.postMessage(data);
		port.onMessage.addListener(function (message) {
			console.log('chat.js: Site name received:');
			console.log(message.site_name);
			resolve(message.site_name);
		});

		site_name = port.onMessage;
		console.log('chat.js: Site name:', site_name);
		return site_name;
	});
}


// Get the latest 10 messages from the server with a GET request
async function getMessages() {
	const site_name = await getSiteName();

	console.log('Getting messages');
	// Fetch the messages from the server
	fetch(get_api_url + site_name)
		.then(response => response.json())
		.then(data => {
			// Clear the chat window
			document.getElementById('chat-window').innerHTML = '';
			// Add each message to the chat window
			data.forEach(message => {
				addMessage(message);
			});
		});
}