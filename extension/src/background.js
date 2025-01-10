console.log('background.js: Background script running');

// Listen for connections
browser.runtime.onConnect.addListener(port => {
	if (port.name === 'get_site_name') {
		port.onMessage.addListener(async message => {
			console.log('background.js: Message from get_site_name port:');
			console.log(message);

			// Get the site name from the current tab
			var site_name = await getSiteName();
			console.log('background.js: Site name sent to port:');
			console.log(site_name);

			// Send the site name back to the content script
			port.postMessage({ site_name: site_name });
		});
	} else if (port.name === 'send_message') {
		port.onMessage.addListener(async message => {
			console.log('background.js: Message from send_message port:');
			console.log(message);

			// Unpack the message object
			var messageContent = message.message;
			var sender_id = message.sender_id;
			var api_token = message.api_token;

			console.log('background.js: Message Content:', messageContent);
			console.log('background.js: Sender ID:', sender_id);
			console.log('background.js: API Token:', api_token);

			// Get the site name asynchronously
			var site_name = await getSiteName();
			console.log('background.js: Site Name:', site_name);

			// Define the URL to send the message to
			const submit_api_url = 'https://127.0.0.1:8080/api/authenticated/';


			// Send the message to the server
			fetch(submit_api_url + site_name, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					message: messageContent,
					site_name: site_name,
					sender_id: sender_id,
					api_token: api_token
				})
			})
				.then(response => {
					if (!response.ok) {
						throw new Error('Network response was not ok');
					}
					return response.json();
				})
				.then(data => {
					console.log('Message sent:', data);
					// Send a response back to the content script
					port.postMessage({ response: 'Message sent', data: data });
				})
				.catch(error => {
					console.error('There was a problem with the fetch operation:', error);
					// Send an error response back to the content script
					port.postMessage({ response: 'Error', error: error.message });
				});
		});
	}
});

function getSiteName() {
	// Return a promise that resolves with the site name
	return new Promise((resolve, reject) => {
		browser.tabs.query({ active: true, currentWindow: true }, function (tabs) {
			if (tabs.length === 0) {
				reject('No active tab found');
				return;
			}
			var tab = tabs[0];
			var site_name = tab.url;
			console.log('background.js: Unclean Site name: ' + site_name);

			// Cleanup the site name to be examplecom instead of https://example.com/anarticle?search=example#example&example
			// regex replace all non-alphanumeric characters with an empty string
			site_name = site_name.split('/')[2];
			site_name = site_name.replace(/[^\w\-\ ]/g, '');
			console.log('background.js: Cleaned Site name: ' + site_name);

			resolve(site_name);
		});
	});
}