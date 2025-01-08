import re
import requests as request
import json
import os
import sqlite3
from flask import Flask, jsonify
import subprocess
import asyncio
from websockets.asyncio.server import serve
import pyotp
import time


# This file will:
# 1. Create a database and table
# 2. Receive data from the clients at /api/ and /ws/ endpoints
# 3. Send data to the clients at /ws/ endpoints
# 4. Insert received data into the table


# The database is based on sqlite3, and who's schema is as follows:
# Site-specific dynamic table:
# CREATE TABLE "<insert sterilized site hostname>" (
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


def main(ADDRESS="0.0.0.0", PORT="8080"):
    print("Starting server...")

# Create a database and table
    conn = sqlite3.connect('rollcall_data.db')
    c = conn.cursor()
    check_database(c)

    # Listen for data with flask
    app = Flask(__name__)

    @app.route('/api/', methods=['POST'])
    def api():
        data = subprocess.request.get_json()
        print(data)
        return jsonify(data)

    @app.route('/ws/', methods=['POST'])
    def ws():
        data = subprocess.request.get_json()
        print(data)
        return jsonify(data)

    app.run(host=ADDRESS, port=PORT)


def check_database(c):

    # Create the users table if it doesn't exist
    c.execute('''CREATE TABLE "users" (
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

    return status


def create_new_user(c, username, email):
    # Cleanup the username and email (remove all non-alphanumeric characters except for periods, dashes, underscores and @ symbols)
    username = re.sub(r'[^a-zA-Z0-9\.\-\_@]', '', username)
    email = re.sub(r'[^a-zA-Z0-9\.\-\_@]', '', email)

    # Create totp secret
    secret = pyotp.random_base32()

    # Create 10 digit epoch time
    epoch_time = int(time.time())

    # Create a new user
    c.execute(f'''INSERT INTO "users" ("username", "registered_date", "email", "hash")
		VALUES ('{username}', {int(epoch_time)}, '{email}', '{secret}')''')

    # check if the user was created
    status = c.execute(
        f"SELECT username FROM users WHERE username='{username}'")

    return status


def create_new_site_table(c, site_name):

    site_name = create_site_name(site_name)

    # Create a table for the site if it doesn't exist
    c.execute(f'''CREATE TABLE "{site_name}" (
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


def create_site_name(site_name):

    # Cleanup the site name (sanitize for SQL injection)
    site_name = re.sub(r'[^a-zA-Z0-9\.\-\_]', '', site_name)

    return site_name


def insert_message(c, site_name, message, sender_id):

    # Cleanup the message (sanitize for SQL injection)
    message = re.sub(r'[^a-zA-Z0-9\.\-\_\s]', '', message)
    site_name = create_site_name(site_name)

    # Create a 10 digit epoch time
    epoch_time = int(time.time())

    # Insert the message into the site table
    c.execute(f'''INSERT INTO "{site_name}" ("message", "sender_id", "time_sent")
		VALUES ('{message}', {sender_id}, {epoch_time})''')

    # check if the message was inserted
    status = c.execute(
        f"SELECT message FROM {site_name} WHERE message='{message}'")

    return status



 
 
ADDRESS = "127.0.0.1"
PORT = "8080"

# Run the main function
main(ADDRESS, PORT)
