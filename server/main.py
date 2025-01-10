import re
import json
# import os
import sqlite3
from flask import Flask, jsonify, request
# import subprocess
# import asyncio
# import pyotp
import time
from flask_cors import CORS


# This file will:
# 1. Create a database and table
# 2. Receive data from the clients at /api/<page> and /ws/<page> endpoints
# 3. Send data to the clients at /ws/<page> endpoints
# 4. Insert received data into the table


# The database is based on sqlite3, and who's schema is as follows:
# Site-specific dynamic table:
# CREATE TABLE "<insert sterilized spip ite hostname>" (
# 	"id"	INTEGER NOT NULL,
# 	"message"	TEXT NOT NULL,
# 	"sender_id"	INTEGER NOT NULL,
# 	"time_sent"	INTEGER NOT NULL,
# 	PRIMARY KEY("id" AUTOINCREMENT)
# )

# User table:
# CREATE TABLE "users" (
#     "id"	INTEGER NOT NULL UNIQUE,
#     "username"	TEXT NOT NULL UNIQUE,
#     "registered_date"	INTEGER NOT NULL,
#     "email"	TEXT NOT NULL UNIQUE,
#     "hash" TEXT NOT NULL,
#     PRIMARY KEY("id" AUTOINCREMENT)
# )

# User email index:
# CREATE INDEX "email_all_users" ON "users" (
# 	"username",
# 	"email"	ASC
# )


def main(ADDRESS="0.0.0.0", PORT="8080", DB_PATH="rollcall_data.db"):
    print("Starting server...")

    # Listen for data with flask
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.route('/api/<page>', methods=['GET'])
    def api(page):
        # Anytime we receive a message, start the database connection
        c = connect_to_database(DB_PATH)

        # page = sitename
        message_history = get_recent_messages(c, page)
        return jsonify(message_history)

    @app.route('/api/authenticated/<page>', methods=['POST', 'OPTIONS'])
    def api_post(page):

        if request.method == 'OPTIONS':
            print("OPTIONS request received")
            # Handle preflight request
            response = app.make_default_options_response()
            headers = response.headers
            headers['Access-Control-Allow-Origin'] = '*'
            headers['Access-Control-Allow-Methods'] = 'OPTIONS, POST'
            headers['Access-Control-Allow-Headers'] = 'Content-Type, api_token'
            return response
        if request.method == 'POST':
            # Get the AUTH_TOKEN from the body
            auth_token = request.json['api_token']

            # Check to see if the AUTH_TOKEN is valid (obviously this is a test token)
            # if check_auth_token(auth_token): eventually we will have a function to check the token with the database populated with tokens from user creation
            if auth_token == "test123testingtesting":
                # Anytime we receive a message, start the database connection
                c = connect_to_database(DB_PATH)

                message = request.json['message']
                if message == "":
                    reason = "message is empty"
                    return jsonify({"status": "failed", "reason": reason})

                sender_id = request.json['sender_id']
                if sender_id == "":
                    reason = "sender_id is empty"
                    return jsonify({"status": "failed", "reason": reason})

                # Insert the message into the database
                status = insert_message(c, page, message, sender_id)

                # Check to see if the message actually got inserted
                if status:
                    return jsonify({"status": "success"})
                else:
                    return jsonify({"status": "failed", "reason": "Unknown error, message may not have been inserted"})
            else:
                print("API token is invalid")
                return jsonify({"status": "unauthorized", "reason": "The API token is somehow missing or incorrect"})

    @app.route('/login', methods=['POST'])
    def login():

        # respond with an api key after successful login FUTURE

        # Anytime we receive a message, start the database connection
        c = connect_to_database(DB_PATH)

        username = request.json['username']
        email = request.json['email']

        # Check if the user exists
        status = c.execute(
            f"SELECT username FROM users WHERE username='{username}' AND email='{email}'")

        # Close the database connection
        close_database_connection(c)

        # Check to see if the user actually exists
        if status.fetchone() is not None:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "failed"})

    @app.route('/register', methods=['POST'])
    def register():

        # Anytime we receive a message, start the database connection
        c = connect_to_database(DB_PATH)

        username = request.json['username']
        email = request.json['email']

        # Create the user
        status = create_new_user(c, username, email)

        # Check to see if the user actually got created
        if status:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "failed"})

    @app.route('/ws/<page>', methods=['GET'])
    def ws(page):
        # page = sitename
        data = get_recent_messages(page)
        return jsonify(data)

    # Thanks https://stackoverflow.com/a/65089126, even though your answer sucked but it works so it didn't suck that much
    @app.errorhandler(404)
    def fof_page_not_found(e):
        # Open the 404 page and return it
        return open("docs/404.html").read()

    @app.errorhandler(405)
    def method_not_allowed(e):
        # Open the 405 page and return it
        return open("docs/405.html").read()

    @app.after_request
    def add_header(response):

        response.headers['Access-Control-Allow-Origin'] = '127.0.0.1:8080'
        response.headers['Access-Control-Allow-Origin'] = 'moz-extension://aaa49584-5f70-4c0e-b8eb-528560d42868'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Allow-Methods'] = '*'
        response.headers['Content-Type'] = 'application/json'
        response.status_code = 200
        # Print all headers
        return response

    app.run(host=ADDRESS, port=PORT, ssl_context=(
        'cert.pem', 'key.pem'))


def connect_to_database(DB_PATH="rollcall_data.db"):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()

    return c


def close_database_connection(c):
    c.connection.commit()
    c.connection.close()


def check_database(c):

    # Create the users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS "users"  (
			"id"	INTEGER NOT NULL UNIQUE,
			"username"	TEXT NOT NULL UNIQUE,
			"registered_date"	INTEGER NOT NULL,
			"email"	TEXT NOT NULL UNIQUE,
			"hash" TEXT NOT NULL,
			PRIMARY KEY("id" AUTOINCREMENT)
		)''')

    # check if the table was created
    status = c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'")

    # Close the database connection
    close_database_connection(c)

    return status


def create_new_user(c, username, email):
    # Cleanup the username and email
    username = santize_SQL_input(username)
    email = sanitize_email(email)

    # Create totp secret
    # secret = pyotp.random_base32()
    secret = "test123testingtesting"

    # Create 10 digit epoch time
    epoch_time = int(time.time())

    # Create a new user
    c.execute(f'''INSERT INTO "users" ("username", "registered_date", "email", "hash")
		VALUES ('{username}', {int(epoch_time)}, '{email}', '{secret}')''')

    # check if the user was created
    status = c.execute(
        f"SELECT username FROM users WHERE username='{username}'")

    # Close the database connection
    close_database_connection(c)

    return status


def create_new_site_table(c, site_name):

    site_name = santize_SQL_input(site_name)

    # Create a table for the site if it doesn't exist
    c.execute(f'''CREATE TABLE IF NOT EXISTS "{site_name}" (
			"id"	INTEGER NOT NULL,
			"message"	TEXT NOT NULL,
			"sender_id"	INTEGER NOT NULL,
			"time_sent"	INTEGER NOT NULL,
			PRIMARY KEY("id" AUTOINCREMENT)
		)''')

    # Create an index on the time_sent column
    c.execute(f'''CREATE INDEX "time_sent_{site_name}" ON "{site_name}" (
			"time_sent"	ASC
		)''')

    # Create an index on the sender_id column
    c.execute(f'''CREATE INDEX "sender_id_{site_name}" ON "{site_name}" (
			"sender_id"	ASC
		)''')

    # check if the table was created
    status = c.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{site_name}'")

    return status


def insert_message(c, site_name, message, sender_id):

    # Cleanup the message (sanitize for SQL injection)
    message = sanitize_message(message)

    # Cleanup the site name (sanitize for SQL injection)
    # from https://stackoverflow.com/a/875978
    site_name = santize_SQL_input(site_name)

    # Create a 10 digit epoch time
    epoch_time = int(time.time())

    # Insert the message into the site table
    c.execute(f'''INSERT INTO "{site_name}" ("message", "sender_id", "time_sent")
		VALUES ('{message}', {sender_id}, {epoch_time})''')

    # check if the message was inserted
    status = c.execute(
        f"SELECT message FROM {site_name} WHERE message='{message}'")

    # Get the first row of the status
    status = status.fetchone()

    if status is not None:
        status = True
    else:
        status = False

    # Close the database connection
    close_database_connection(c)

    return status


def get_recent_messages(c, site_name):

    # Santize and standardize the site name
    site_name = santize_SQL_input(site_name)

    # Check if the site table exists
    table_exists = c.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{site_name}'")
    # convert into a boolean
    table_exists = table_exists.fetchone()
    if table_exists is not None:
        table_exists = True
    else:
        table_exists = False
        create_new_site_table(c, site_name)

    # Get the 10 most recent messages from the site table
    messages = c.execute(
        f"SELECT id, message FROM {site_name} ORDER BY time_sent DESC LIMIT 15")

    # sanitize the messages for output as html
    messages = messages.fetchall()
    for i in range(len(messages)):
        messages[i] = sanitize_html(messages[i][1])

    # Close database
    close_database_connection(c)

    return messages


# Thanks https://stackoverflow.com/a/875978
def santize_SQL_input(input):
    # Santize the input for SQL injection
    input = re.sub(r'[^\w\-\ ]', '', input)
    return input


def sanitize_html(input):
    # Santize the input for HTML injection
    input = re.sub(r'[^\w\.\-\_\s]', '', input)
    return input


def sanitize_email(input):
    # Santize the input for email injection
    input = re.sub(r'[^\w\.\-\_@]', '', input)
    return input


def sanitize_message(input):
    # Santize the input for message injection
    input = re.sub(r'[^\w\.\-\s\?\!]', '', input)
    return input


ADDRESS = "127.0.0.1"
PORT = "8080"
DB_PATH = "rollcall_data.db"

# Run the main function
main(ADDRESS, PORT, DB_PATH)

# Close the database connection
c = connect_to_database(DB_PATH="rollcall_data.db")
close_database_connection(c)
