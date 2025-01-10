venv:
	@echo "Removing old venv"
	rm -rf .venv
	@echo "Creating new venv"
	python3 -m venv .venv
	@echo "Activating venv"
	source $(pwd)/.venv/bin/activate

setup: venv certs
	pip install -r requirements.txt
	sudo apt install sqlite3 libsqlite3-dev python3-full openssl

certs: 
	openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

run: setup
	python3 main.py
