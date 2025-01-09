// This script controls the chat functionality of the extension.
// It listens for, sends, and displays messages in the chat window

// Get the current url of the page
// var currentUrl = window.location.href;

// // Strip it down to the base url (no query parameters, protocol, or hash)
// var baseUrl = currentUrl.split('?')[0].split('#')[0];

// // Get the current domain of the page
// var site_name = baseUrl.split('/')[2];
// console.log(site_name);

// Set the site_name to a testing name so we don't have to muck about
// with about:debugging#/runtime/this-firefox
site_name = "firefoxabout.com";

const api_url = 'https://10.0.0.9:8085/api/';

// Get the latest 10 messages from the server with a GET request
function getMessages() {
	console.log('Getting messages');
	// Fetch the messages from the server
	fetch(api_url + site_name)
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

document.onload = getMessages();

// Add a message to the chat window
function addMessage(message) {
	// Create a new div element
	var newMessage = document.createElement('div');
	// Add the message to the div
	newMessage.innerHTML = message;
	// Add the div to the chat window
	document.getElementById('chat-window').appendChild(newMessage);
}


// Send a message to the server with a POST request
function sendMessage() {

	// Set the sender_id to a random number between 1 and 1,000,000
	var sender_id = Math.floor(Math.random() * 1000000);

	// set the api_token to a testing string
	var api_token = "test123testingtesting";

	// Get the message from the input field
	var message = document.getElementById('message-input').value;
	// Clear the input field
	document.getElementById('message-input').value = '';
	// Send the message to the server
	fetch(api_url + site_name, {
		method: 'POST',
		body: JSON.stringify({ message: message, site_name: site_name, sender_id: sender_id }),
		headers: {
			'Content-Type': 'application/json',
			'Access-Control-Allow-Origin': '*',
		}
	})
		.then(response => response.json())
		.then(data => {
			// Add the message to the chat window
			addMessage(data.message);
		});
}