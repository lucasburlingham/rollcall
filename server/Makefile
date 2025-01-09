venv:
	python3 -m venv .venv
	source .venv/bin/activate

setup: venv
	pip install -r requirements.txt
	sudo apt install sqlite3 libsqlite3-dev python3-full

run: setup
	python3 main.py
