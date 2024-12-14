import sqlite3
import json
import os

# Caminho para o arquivo do banco de dados SQLite
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'football_data.db')

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
    return conn

def create_table():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER UNIQUE,
                    data TEXT
                )
            ''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar tabela: {e}")
        finally:
            conn.close()

def save_match_data_sqlite(match_id, data):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO matches (match_id, data) VALUES (?, ?)",
                           (match_id, json.dumps(data)))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao salvar dados no SQLite: {e}")
        finally:
            conn.close()
    return None

def get_saved_match_data_sqlite(match_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, match_id FROM matches WHERE match_id = ?", (match_id,))
            result = cursor.fetchone()
            if result:
                return {"_id": result[0], "match_id": result[1]}
        except sqlite3.Error as e:
            print(f"Erro ao recuperar dados do SQLite: {e}")
        finally:
            conn.close()
    return None

# Criar a tabela ao importar o módulo
create_table()