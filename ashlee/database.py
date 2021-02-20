import os
import sqlite3


class User:
    def __init__(self, row):
        self.id, self.first_name, self.last_name, self.username, \
            self.language, self.status, self.lemons, self.date_time = row


class Chat:
    def __init__(self, row):
        self.chat_id, self.type, self.title, self.username, self.admins, self.date_time = row
        self.admins = set(map(int, self.admins.split(',')))


class Database:

    SQL_DB_EXISTS = 'SELECT name FROM sqlite_master'
    SQL_CREATE_USERS = '''CREATE TABLE users (
        user_id INTEGER NOT NULL PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT,
        username TEXT,
        language TEXT,
        status INTEGER NOT NULL DEFAULT 1,
        lemons INTEGER NOT NULL DEFAULT 0,
        date_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''
    SQL_CREATE_CHATS = '''CREATE TABLE chats (
        chat_id INTEGER NOT NULL PRIMARY KEY,
        type TEXT NOT NULL,
        title TEXT,
        username TEXT,
        admins TEXT DEFAULT NULL,
        date_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''
    SQL_CREATE_CMD_DATA = '''CREATE TABLE cmd_data (
        user_id INTEGER NOT NULL,
        chat_id INTEGER,
        command TEXT NOT NULL,
        date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
    )'''

    SQL_USER_EXISTS = '''SELECT EXISTS (
        SELECT 1 FROM users WHERE user_id = ?
    )'''
    SQL_USER_ADD = 'INSERT INTO users (user_id, first_name, last_name, username, language) VALUES (?, ?, ?, ?, ?)'
    SQL_USER_UPDATE = 'UPDATE users SET first_name = ?, last_name = ?, username = ?, language = ? WHERE user_id = ?'
    SQL_USER_GET = 'SELECT user_id, first_name, last_name, username, language, status, lemons, date_time ' \
                   'FROM users WHERE user_id = ?'

    SQL_CHAT_EXISTS = '''SELECT EXISTS (
        SELECT 1 FROM chats WHERE chat_id = ?
    )'''
    SQL_CHAT_ADD = 'INSERT INTO chats (chat_id, type, title, username) VALUES (?, ?, ?, ?)'
    SQL_CHAT_UPDATE = 'UPDATE chats SET type = ?, title = ?, username = ? WHERE chat_id = ?'
    SQL_CHAT_GET = 'SELECT chat_id, type, title, username, admins, date_time FROM chats WHERE chat_id = ?'

    SQL_CMD_ADD = 'INSERT INTO cmd_data (user_id, chat_id, command) VALUES (?, ?, ?)'

    # Initialize database
    def __init__(self, db_path):
        self._db_path = db_path

        # Create 'data' directory if not present
        data_dir = os.path.dirname(db_path)
        os.makedirs(data_dir, exist_ok=True)

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # If tables don't exist, create them
        if not cur.execute(self.SQL_DB_EXISTS).fetchone():
            cur.execute(self.SQL_CREATE_USERS)
            con.commit()
            cur.execute(self.SQL_CREATE_CHATS)
            con.commit()
            cur.execute(self.SQL_CREATE_CMD_DATA)
            con.commit()

            con.close()

    # Save user and / or chat to database
    def save_user_and_chat(self, user, chat):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        # Check if user already exists
        cur.execute(self.SQL_USER_EXISTS, [user.id])
        # Add user if he doesn't exist
        if cur.fetchone()[0] != 1:
            cur.execute(self.SQL_USER_ADD,
                        (user.id, user.first_name, user.last_name, user.username, user.language_code))
            con.commit()
        else:
            cur.execute(self.SQL_USER_UPDATE,
                        (user.first_name, user.last_name, user.username, user.language_code, user.id))
            con.commit()

        chat_id = None

        if chat and chat.id != user.id:
            chat_id = chat.id

            # Check if chat already exists
            cur.execute(self.SQL_CHAT_EXISTS, (chat.id, ))

            con.commit()

            # Add chat if it doesn't exist
            if cur.fetchone()[0] != 1:
                cur.execute(self.SQL_CHAT_ADD, (chat.id, chat.type, chat.title, chat.username))
                con.commit()
            else:
                cur.execute(self.SQL_CHAT_UPDATE, (chat.type, chat.title, chat.username, chat.id))
                con.commit()

        con.close()

        return user.id, chat_id

    def save_cmd(self, user, chat, cmd):
        user_id, chat_id = self.save_user_and_chat(user, chat)

        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        # Save issued command
        cur.execute(self.SQL_CMD_ADD, (user_id, chat_id, cmd))

        con.commit()
        con.close()

    def get_user(self, user_id) -> User:
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        cur.execute(self.SQL_USER_GET, (user_id, ))
        row = cur.fetchone()
        con.close()
        return User(row)

    def get_chat(self, chat_id) -> Chat:
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        cur.execute(self.SQL_CHAT_GET, (chat_id, ))
        row = cur.fetchone()
        con.close()
        return Chat(row)
