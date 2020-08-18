import psycopg2
from psycopg2.extras import DictCursor
from enum import Enum


class Command(Enum):
    CREATE_USER = 1
    RESET_USER = 2
    DELETE_USER = 3
    SET_CITY = 4
    GET_CITY = 5
    GET_COUNT = 6


def _get_connection(config):
    conn = psycopg2.connect(dbname=config.db_name,
                            user=config.login,
                            password=config.password,
                            host=config.host)
    return conn


def _get_user(cursor, chat_id):
    cursor.execute(f"SELECT * FROM users WHERE chat_id = {chat_id}")
    users = cursor.fetchall()
    if not users:
        return None
    else:
        return users[0]


def _insert(cursor, chat_id):
    cursor.execute(f"INSERT INTO users (chat_id, city) VALUES ({chat_id}, NULL)")


def _update(cursor, chat_id, city=None):
    if city is None:
        cursor.execute(f"UPDATE users SET city = NULL WHERE chat_id = {chat_id}")
    else:
        cursor.execute(f"UPDATE users SET city = '{city}' WHERE chat_id = {chat_id}")


def _delete(cursor, chat_id):
    cursor.execute(f"DELETE FROM users WHERE chat_id = {chat_id}")


def _count(cursor):
    cursor.execute(f"SELECT * FROM users")
    return len(cursor.fetchall())


def query(config, chat_id, command, city=None):
    with _get_connection(config) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            user = _get_user(cursor, chat_id)
            if command == Command.CREATE_USER:
                if user is None:
                    _insert(cursor, chat_id)
                    return True
                else:
                    return False
            elif command == Command.RESET_USER:
                if user is None:
                    return False
                else:
                    _update(cursor, chat_id)
                    return True
            elif command == Command.DELETE_USER:
                if user is None:
                    return False
                else:
                    _delete(cursor, chat_id)
                    return True
            elif command == Command.SET_CITY:
                if user is None or city is None:
                    return False
                else:
                    _update(cursor, chat_id, city)
                    return True
            elif command == Command.GET_CITY:
                if user is None:
                    return False
                else:
                    return user['city']
            elif command == Command.GET_COUNT:
                return _count(cursor)
