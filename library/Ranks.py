from telegram import TelegramError
from telegram.ext import BaseFilter

from objects import dbmanager


class permission(BaseFilter):
    """
    This is a cumstom filter class to be used with a MessageHandler object of the python-telegram-bot module.
    """

    def __init__(self, perm):
        self.perm = perm
        return

    def filter(self, message):
        flag = False
        tg_user = message.from_user
        rankable = Rankable(tg_user)
        if rankable.has_permission(self.perm):
            flag = True
        return flag


def create_db_tables():
    conn, c = dbmanager.get_connection()
    c.execute('CREATE TABLE IF NOT EXISTS users_ranks (id SERIAL, user_id BIGINT, rank VARCHAR(30), '
              'PRIMARY KEY(user_id, rank))')
    c.execute('CREATE TABLE IF NOT EXISTS ranks (id SERIAL, name VARCHAR(30) PRIMARY KEY, hierarchy INTEGER)')
    # Allow permission is 1 for Allow, and 0 for deny
    c.execute('CREATE TABLE IF NOT EXISTS rank_permissions (id SERIAL, rank VARCHAR(30), permission VARCHAR(20), '
              'allow BOOL,'
              'PRIMARY KEY(rank, permission))')
    c.execute('CREATE TABLE IF NOT EXISTS user_permissions (id SERIAL, user_id BIGINT, permission VARCHAR(20), '
              'allow BOOL,'
              'PRIMARY KEY(user_id, permission))')
    conn.commit()
    conn.close()
    return


def get_users_by_rank(rank):
    """
    Parameters:
        rank (string): Name of the rank.

    Return (list): List with id of all users that belongs to rank.
    """
    conn, c = dbmanager.get_connection()
    vector = []
    query = "SELECT user_id FROM users_ranks WHERE rank = '{}'".format(rank)
    c.execute(query)
    results = c.fetchall()
    for value in results:
        user_id = value["user_id"]
        vector.append(user_id)
    c.close()
    conn.close()
    return vector


def add_rank(name, hierarchy):
    """
    Add a new rank to the database.

    Parameters:
        name (string): Name of the rank.
        hierarchy (integer): Number of hierarchy.
    """
    conn, c = dbmanager.get_connection()
    query = "INSERT INTO ranks(name, hierarchy) VALUES(%s, %s) ON CONFLICT DO NOTHING"
    c.execute(query, (name, hierarchy))
    conn.commit()
    c.close()
    conn.close()
    return


def add_rank_permission(rank, permission_string, boolean):
    """
    Add a new permission to an existing rank.

    Parameters:
        rank (string): Name of the rank.
        permission_string (string): Permission to add.
        boolean (integer) (Optional): 1 for enable the permission, 0 for disable. Default: 1.
    """
    conn, c = dbmanager.get_connection()
    if boolean != 1 and boolean != 0:
        boolean = 1
    query = "INSERT INTO rank_permissions(rank, permission, allow) VALUES(%s, %s, %s) ON CONFLICT DO NOTHING"
    c.execute(query, (rank, permission_string, bool(boolean)))
    conn.commit()
    c.close()
    conn.close()
    return


def add_user_rank(user_id, rank):
    """
    Add a rank to a user.
    Parameters:
        user_id (integer): Id of the user affected.
        rank (string): New rank for the user.
    """
    conn, c = dbmanager.get_connection()
    query = "INSERT INTO users_ranks(user_id, rank) VALUES(%s, %s) ON CONFLICT DO NOTHING"
    c.execute(query, (user_id, rank))
    conn.commit()
    c.close()
    conn.close()
    return


def remove_user_rank(user_id, rank):
    """
    Remove a rank from a user.
    Parameters:
        user_id (integer): Id of the user affected.
        rank (string): Name of the rank to be removed from the user.
    """
    conn, c = dbmanager.get_connection()
    query = "DELETE FROM users_ranks WHERE user_id = %s AND rank = %s"
    c.execute(query, (user_id, rank))
    conn.commit()
    c.close()
    conn.close()
    return


class Rankable:
    """
    This class represents an object that can have a rank and permissions.
    """

    def __init__(self, tg_user=None, tg_id=None, bot=None):
        """
        Parameters:
        """
        if tg_user:
            self.tg_user = tg_user
            self.tg_id = tg_user.id
        elif tg_id and bot:
            try:
                self.tg_user = bot.get_chat_member(chat_id=tg_id, user_id=tg_id).user
            except TelegramError as error:
                print(error)
                self.tg_user = None
                self.tg_id = tg_id
        else:
            raise Exception("Can not create User object")
        return

    def has_permission(self, permission_string):
        """
        Parameters:
            permission_string (string): The permission to test with the rankable object.
        Return:
            True if the rankable object has the permission active.
        """
        conn, c = dbmanager.get_connection()
        query = "SELECT allow FROM user_permissions WHERE permission = %s AND user_id = %s"
        c.execute(query, (permission_string, self.tg_id))
        result = c.fetchone()
        c.close()
        conn.close()
        if result is not None:
            if result["allow"] == 1:
                return True
            elif result["allow"] == 0:
                return False
        conn, c = dbmanager.get_connection()
        query = "SELECT ranks.name FROM users_ranks INNER JOIN ranks ON users_ranks.rank = ranks.name WHERE " \
                "users_ranks.user_id = %s ORDER BY ranks.hierarchy DESC"
        c.execute(query, (self.tg_id,))
        results = c.fetchall()
        if len(results) == 0:  # If the user have no rank assigned
            c.close()
            conn.close()
            return False
        for value in results:
            rank = value["name"]
            query = "SELECT allow FROM rank_permissions WHERE permission = %s AND rank = %s"
            c.execute(query, (permission_string, rank))
            results = c.fetchone()
            if results is not None:
                if results["allow"] == 1:
                    return True
                elif results["allow"] == 0:
                    return False
        c.close()
        conn.close()
        return False

    def add_permission(self, permission_string, boolean=True):
        """
        Parameters
            permission (string): The permission to add to the user.
            boolean (integer): True for active. False for deactive.
        """
        conn, c = dbmanager.get_connection()
        boolean = bool(boolean)
        query_1 = "INSERT INTO user_permissions(user_id, permission, allow) VALUES(%s, %s, %s) ON CONFLICT DO NOTHING"
        c.execute(query_1, (self.tg_id, permission_string, bool(boolean)))
        query_2 = "UPDATE user_permissions SET allow = %s WHERE permission = %s AND user_id = %s"
        c.execute(query_2, (bool(boolean), permission_string, self.tg_id))
        conn.commit()
        c.close()
        conn.close()
        return

    def add_rank(self, rank):
        """
        Add a rank to a user.
        Parameters:
            rank (string): New rank for the user.
        """
        add_user_rank(self.tg_id, rank)
        return

    def remove_rank(self, rank):
        """
        Remove a rank from a user.
        Parameters:
            rank (string): Name of the rank to be removed from the user.
        """
        remove_user_rank(self.tg_id, rank)
        return

    def ranks(self):
        """
        :return: (String list) List with the ranks of the entity with descending order of hierarchy.
        """
        conn, c = dbmanager.get_connection()
        query = "SELECT ranks.name FROM users_ranks INNER JOIN ranks ON users_ranks.rank = ranks.name " \
                "WHERE users_ranks.user_id = %s ORDER BY ranks.hierarchy DESC"
        c.execute(query, (self.tg_id,))
        result = c.fetchall()
        c.close()
        conn.close()
        rank_list = []
        for row in result:
            rank_list.append(row["name"])
        return rank_list

    def is_rank(self, rank):
        conn, c = dbmanager.get_connection()
        query = "SELECT * FROM users_ranks WHERE user_id = %s AND rank = %s"
        c.execute(query, (self.tg_id, rank))
        value = c.fetchone()
        c.close()
        conn.close()
        if value is not None:
            return True
        return False
