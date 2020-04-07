import os

from library.Ranks import Rankable
from objects import dbmanager


class User(Rankable):
    def __init__(self, tg_user=None, tg_id=None, bot=None):
        super().__init__(tg_user, tg_id, bot)
        return

    def is_registered(self):
        conn, c = dbmanager.get_connection()
        query = "SELECT id FROM users WHERE tg_id = %s"
        c.execute(query, (self.tg_id,))
        result = c.fetchone()
        conn.close()
        c.close()
        if result:
            return True
        return False

    def register(self):
        conn, c = dbmanager.get_connection()
        query = "INSERT INTO users(tg_id, first_name, last_name, username, language_code) " \
                "VALUES(%s, %s, %s, %s, %s) ON CONFLICT(tg_id) DO UPDATE SET first_name = %s, " \
                "last_name = %s, " \
                "username = %s, " \
                "language_code = %s"
        data = (self.tg_id, self.first_name, self.last_name, self.username, self.language_code,
                self.first_name, self.last_name, self.username, self.language_code)
        c.execute(query, data)
        conn.commit()
        conn.close()
        c.close()
        return

    @property
    def first_name(self):
        if self.tg_user:
            return self.tg_user.first_name
        else:
            conn, c = dbmanager.get_connection()
            query = "SELECT first_name FROM users WHERE tg_id = %s"
            c.execute(query, (self.tg_id,))
            result = c.fetchone()
            c.close()
            conn.close()
            if result:
                return result["first_name"]
        return None

    @property
    def last_name(self):
        if self.tg_user:
            return self.tg_user.last_name
        else:
            conn, c = dbmanager.get_connection()
            query = "SELECT last_name FROM users WHERE tg_id = %s"
            c.execute(query, (self.tg_id,))
            result = c.fetchone()
            c.close()
            conn.close()
            if result:
                return result["last_name"]
        return None

    @property
    def username(self):
        if self.tg_user:
            return self.tg_user.username
        else:
            conn, c = dbmanager.get_connection()
            query = "SELECT username FROM users WHERE tg_id = %s"
            c.execute(query, (self.tg_id,))
            result = c.fetchone()
            c.close()
            conn.close()
            if result:
                return result["username"]
        return None

    @property
    def language_code_in_bot(self):
        conn, c = dbmanager.get_connection()
        query = "SELECT language_code_in_bot FROM users WHERE tg_id = %s"
        c.execute(query, (self.tg_id,))
        result = c.fetchone()
        c.close()
        conn.close()
        if result:
            return result["language_code_in_bot"]
        return "default"

    @language_code_in_bot.setter
    def language_code_in_bot(self, code):
        conn, c = dbmanager.get_connection()
        query = "UPDATE users SET language_code_in_bot = %s WHERE tg_id = %s"
        c.execute(query, (code, self.tg_id))
        conn.commit()
        c.close()
        conn.close()
        return

    @property
    def language_code(self):
        if self.tg_user:
            return self.tg_user.language_code
        else:
            conn, c = dbmanager.get_connection()
            query = "SELECT language_code FROM users WHERE tg_id = %s"
            c.execute(query, (self.tg_id,))
            result = c.fetchone()
            c.close()
            conn.close()
            if result:
                return result["language_code"]
        return None

    def is_owner(self):
        owner_id = os.environ['OWNER_ID'].split(",")
        if str(self.tg_id) in owner_id:
            return True
        return False

    def addtag(self, tag):
        conn, c = dbmanager.get_connection()
        query = "INSERT INTO user_tags(user_id, tag) VALUES(" \
                "(SELECT id FROM users WHERE tg_id = %s), %s) ON CONFLICT(user_id, tag) DO NOTHING"
        data = (self.tg_id, tag)
        c.execute(query, data)
        conn.commit()
        c.close()
        conn.close()
        return
