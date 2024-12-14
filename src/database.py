import os
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import quote_plus
import sqlite3

load_dotenv()

def get_env_variable(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"A variável de ambiente {var_name} não está definida.")
    return value

def create_mongodb_client():
    try:
        mongodb_user = get_env_variable('MONGODB_USER')
        mongodb_password = get_env_variable('MONGODB_PASSWORD')
        mongodb_host = get_env_variable('MONGODB_HOST')
        mongodb_port = get_env_variable('MONGODB_PORT')
        mongodb_database = get_env_variable('MONGODB_DATABASE')

        mongodb_uri = f"mongodb://{quote_plus(mongodb_user)}:{quote_plus(mongodb_password)}@{mongodb_host}:{mongodb_port}/{mongodb_database}"

        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Aviso: Não foi possível conectar ao MongoDB. Erro: {e}")
        return None

def get_database_collection():
    client = create_mongodb_client()
    if client:
        db_name = get_env_variable('MONGODB_MAIN_DB')
        collection_name = get_env_variable('MONGODB_USER_COLLECTION')
        return client[db_name][collection_name]
    else:
        return None

collection = get_database_collection()



SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'football_data.db')

def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB_PATH)

def create_sqlite_table():
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER UNIQUE,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_sqlite_table()