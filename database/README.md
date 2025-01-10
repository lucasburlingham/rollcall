# Database setup

This is a simple SQLite database that looks like the following:

```sql
-- Site-specific dynamic table:
CREATE TABLE "<insert sterilized site hostname>" (
    "id"        INTEGER NOT NULL,
    "message"   TEXT NOT NULL,
    "sender_id" INTEGER NOT NULL,
    "time_sent" INTEGER NOT NULL,
    KEY("id" AUTOINCREMENT)
)

-- User table:
CREATE TABLE "users" (
    "id"               INTEGER NOT NULL UNIQUE,
    "username"         TEXT NOT NULL UNIQUE,
    "registered_date"  INTEGER NOT NULL,
    "email"            TEXT NOT NULL UNIQUE,
    "hash"             TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)

-- User email index:
CREATE INDEX "email_all_users" ON "users" (
    "username",
    "email"     ASC
)

```

The database is by default named `rollcall.db` and is located in the same directory as `main.py`. The database and tables are created at server startup if they don't already exist. The database is accessed using the `sqlite3` module in Python.
