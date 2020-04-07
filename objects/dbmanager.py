import os

import psycopg2
from pony.orm import Database
from psycopg2.extras import RealDictCursor

import settings


def get_connection():
    """
    Return (sql connection, sql cursor): Connection for the general database.
    """
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor(cursor_factory=RealDictCursor)
    return conn, c


def create_tables():
    conn, c = get_connection()
    c.execute('CREATE TABLE IF NOT EXISTS users (id SERIAL UNIQUE, tg_id BIGINT UNIQUE, '
              'first_name TEXT, last_name TEXT, username TEXT, language_code TEXT, language_code_in_bot TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS languages (id SERIAL, name TEXT UNIQUE, code TEXT UNIQUE, '
              'file_id TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS chatflows (id SERIAL, name TEXT UNIQUE, file_id TEXT UNIQUE)')
    c.execute("CREATE TABLE IF NOT EXISTS user_tags(id SERIAL, "
              "user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, "
              "tag TEXT, "
              "CONSTRAINT unq_tag UNIQUE(user_id, tag))")
    c.execute("CREATE TABLE IF NOT EXISTS configuration(id SERIAL, name TEXT UNIQUE, value TEXT)")
    conn.commit()
    c.close()
    conn.close()
    return


def initialize_database():
    database = Database()
    settings.database = database
    define_entities()
    user, password, host, database_name = split_url(os.getenv('DATABASE_URL'))
    database.bind(provider='postgres', user=user, password=password, host=host, database=database_name)
    return


def define_entities():
    """
    Initialize database entities
    :return:
    """
    database = settings.database
    return


def split_url(url):
    """
    Return user, password, host and database from a database url.
    :return:
    """
    try:
        url = url[13:]
        user = url.split(":")[0]
        password = url.split(":")[1].split("@")[0]
        host = url.split(":")[1].split("@")[1].split("/")[0]
        database = url.split(":")[1].split("@")[1].split("/")[1]
    except IndexError:
        return None
    else:
        return user, password, host, database
