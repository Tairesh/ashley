import os
import sqlite3


class User:
    def __init__(self, row):
        self.id, self.first_name, self.last_name, self.username, \
            self.language, self.status, self.lemons, self.date_time = row


class Chat:
    def __init__(self, row):
        self.chat_id, self.type, self.title, self.username, self.users, self.date_time = row
        self.users = set(map(int, self.users.split(','))) if self.users else set()


class ChatSettings:
    def __init__(self, row):
        self.chat_id, self.language, self.enabled_porn, self.enabled_anime, self.enabled_replies, \
            self.welcome_photo, self.welcome_message, self.welcome_buttons, self.welcome_restrict = row
        self.welcome_buttons = self.welcome_buttons.split(',') if self.welcome_buttons else []


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
    SQL_CREATE_USERS_INDEX = '''CREATE UNIQUE INDEX IF NOT EXISTS users_username ON users (username)'''
    SQL_CREATE_CHATS = '''CREATE TABLE chats (
        chat_id INTEGER NOT NULL PRIMARY KEY,
        type TEXT NOT NULL,
        title TEXT,
        username TEXT,
        users TEXT DEFAULT NULL,
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
    SQL_CREATE_CHATS_SETTINGS = '''CREATE TABLE chats_settings (
        chat_id INTEGER NOT NULL PRIMARY KEY,
        language TEXT DEFAULT NULL,
        enabled_porn INTEGER NOT NULL DEFAULT 1,
        enabled_anime INTEGER NOT NULL DEFAULT 1,
        enabled_replies INTEGER NOT NULL DEFAULT 1,
        welcome_photo TEXT DEFAULT NULL,
        welcome_message TEXT DEFAULT NULL,
        welcome_buttons TEXT DEFAULT NULL,
        welcome_restrict INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
    )'''

    SQL_USER_EXISTS = '''SELECT EXISTS (
        SELECT 1 FROM users WHERE user_id = ?
    )'''
    SQL_USER_ADD = 'INSERT INTO users (user_id, first_name, last_name, username, language) VALUES (?, ?, ?, ?, ?)'
    SQL_USER_UPDATE = 'UPDATE users SET first_name = ?, last_name = ?, username = ?, language = ? WHERE user_id = ?'
    SQL_USER_UPDATE_LEMONS = 'UPDATE users SET lemons = ? WHERE user_id = ?'
    SQL_USER_GET = 'SELECT user_id, first_name, last_name, username, language, status, lemons, date_time ' \
                   'FROM users WHERE user_id = ?'
    SQL_USER_GET_BY_UN = 'SELECT user_id, first_name, last_name, username, language, status, lemons, date_time ' \
                         'FROM users WHERE lower(username) = ?'

    SQL_CHAT_EXISTS = '''SELECT EXISTS (
        SELECT 1 FROM chats WHERE chat_id = ?
    )'''
    SQL_CHAT_ADD = 'INSERT INTO chats (chat_id, type, title, username) VALUES (?, ?, ?, ?)'
    SQL_CHAT_UPDATE = 'UPDATE chats SET type = ?, title = ?, username = ? WHERE chat_id = ?'
    SQL_CHAT_GET = 'SELECT chat_id, type, title, username, users, date_time FROM chats WHERE chat_id = ?'
    SQL_CHAT_UPDATE_USERS = 'UPDATE chats SET users = ? WHERE chat_id = ?'

    SQL_CMD_ADD = 'INSERT INTO cmd_data (user_id, chat_id, command) VALUES (?, ?, ?)'

    SQL_GET_CHATS_SETTINGS = 'SELECT chat_id, language, enabled_porn, enabled_anime, enabled_replies, ' \
                             'welcome_photo, welcome_message, welcome_buttons, welcome_restrict ' \
                             'FROM chats_settings WHERE chat_id = ?'
    SQL_CHAT_SETTINGS_ADD = 'INSERT INTO chats_settings (chat_id, language) VALUES (?, ?)'
    SQL_CHAT_SETTINGS_UPDATE = 'UPDATE chats_settings SET enabled_porn = ?, enabled_anime = ?, enabled_replies = ?, ' \
                               'welcome_photo = ?, welcome_message = ?, welcome_buttons = ?, welcome_restrict = ? ' \
                               'WHERE chat_id = ?'

    # Initialize database
    def __init__(self, db_path):
        self._db_path = db_path

        # Create 'data' directory if not present
        data_dir = os.path.dirname(db_path)
        os.makedirs(data_dir, exist_ok=True)

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # If tables don't exist, create them
        tables = set([row[0] for row in cur.execute(self.SQL_DB_EXISTS).fetchall()])
        if 'users' not in tables:
            cur.execute(self.SQL_CREATE_USERS)
            con.commit()
        cur.execute(self.SQL_CREATE_USERS_INDEX)
        if 'chats' not in tables:
            cur.execute(self.SQL_CREATE_CHATS)
            con.commit()
        if 'cmd_data' not in tables:
            cur.execute(self.SQL_CREATE_CMD_DATA)
            con.commit()
        if 'chats_settings' not in tables:
            cur.execute(self.SQL_CREATE_CHATS_SETTINGS)
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

            chat = self.get_chat(chat_id)
            if user.id not in chat.users:
                chat.users.add(user.id)
                cur.execute(self.SQL_CHAT_UPDATE_USERS, [','.join((str(u) for u in chat.users)), chat_id])
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
        return User(row) if row else None

    def get_user_by_username(self, username) -> User:
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        cur.execute(self.SQL_USER_GET_BY_UN, (username, ))
        row = cur.fetchone()
        con.close()
        return User(row) if row else None

    def get_chat(self, chat_id) -> Chat:
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        cur.execute(self.SQL_CHAT_GET, (chat_id, ))
        row = cur.fetchone()
        con.close()
        return Chat(row) if row else None

    def get_chat_settings(self, chat_id) -> ChatSettings:
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        cur.execute(self.SQL_GET_CHATS_SETTINGS, (chat_id, ))
        row = cur.fetchone()
        con.close()
        return ChatSettings(row) if row else None

    def add_chat_settings(self, chat_id):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        cur.execute(self.SQL_CHAT_SETTINGS_ADD, (chat_id, 'ru'))
        con.commit()
        con.close()

    def update_chat_settings(self, chat_id, enabled_porn=1, enabled_anime=1, enabled_replies=1,
                             welcome_photo=None, welcome_message=None, welcome_buttons=None, welcome_restrict=0):
        if welcome_buttons is not None:
            if len(welcome_buttons):
                welcome_buttons = ','.join(welcome_buttons)
            else:
                welcome_buttons = None
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        cur.execute(self.SQL_CHAT_SETTINGS_UPDATE, (enabled_porn, enabled_anime, enabled_replies,
                                                    welcome_photo, welcome_message, welcome_buttons, welcome_restrict,
                                                    chat_id))
        con.commit()
        con.close()

    def update_user_lemons(self, user_id, lemons):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        cur.execute(self.SQL_USER_UPDATE_LEMONS, (lemons, user_id))
        con.commit()
        con.close()
