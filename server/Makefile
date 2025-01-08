venv:
	. .venv/bin/activate

setup: venv
	pip install -r requirements.txt
	sudo apt install sqlite3 libsqlite3-dev

run: setup
	python3 main.py
