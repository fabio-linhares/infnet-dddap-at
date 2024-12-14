import json
import numpy as np
import datetime
from bson import json_util
from statsbombpy import sb
from src.database import collection, get_sqlite_connection
from pymongo import ReturnDocument
import sqlite3


def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {convert_numpy_types(key): convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bytes_, bytes)):
        return obj.decode('utf-8')
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif obj is None:
        return None
    elif hasattr(obj, 'item'):
        return obj.item()
    elif hasattr(obj, 'to_dict'):
        return convert_numpy_types(obj.to_dict())
    else:
        return str(obj)


def get_competitions():
    return sb.competitions()

def get_matches(competition_id, season_id):
    return sb.matches(competition_id=competition_id, season_id=season_id)

def get_match_data(match_id):
    try:
        match_data = sb.events(match_id=match_id)
        if not match_data.empty:
            data_dict = match_data.to_dict(orient='records')
            return convert_numpy_types(data_dict)
        return {}
    except Exception as e:
        print(f"Erro ao obter dados da partida: {e}")
        return {}

def save_match_data(match_id, data):
    if collection:
        try:
            print("Verificando a existência de dados...")
            match_id_int = int(match_id)
            existing_data = collection.find_one({"match_id": match_id_int}, projection={"_id": 1, "match_id": 1})
            
            if existing_data:
                print("Dados já existem. Atualizando...")
                result = collection.update_one(
                    {"match_id": match_id_int},
                    {"$set": {"data": convert_numpy_types(data)}}
                )
                if result.modified_count > 0:
                    print("Dados atualizados com sucesso.")
                    return str(existing_data['_id']), int(existing_data['match_id'])
                else:
                    print("Nenhuma alteração foi necessária.")
                    return str(existing_data['_id']), int(existing_data['match_id'])
            else:
                print("Dados não existem. Inserindo novos dados...")
                converted_data = convert_numpy_types(data)
                result = collection.insert_one({"match_id": match_id_int, "data": converted_data})
                print("Inserção no MongoDB concluída.")
                return str(result.inserted_id), match_id_int
        except Exception as e:
            print(f"Erro ao salvar no MongoDB: {e}. Tentando SQLite...")
            return save_match_data_sqlite(match_id, data)
    else:
        return save_match_data_sqlite(match_id, data)




def get_saved_match_data(match_id):
    if collection:
        try:
            match_id_int = int(match_id)
            result = collection.find_one({"match_id": match_id_int})
            if result:
                return {
                    "_id": str(result["_id"]),
                    "match_id": int(result["match_id"])
                }
            return None
        except Exception as e:
            print(f"Erro ao recuperar do MongoDB: {e}. Tentando SQLite...")
            return get_saved_match_data_sqlite(match_id)
    else:
        return get_saved_match_data_sqlite(match_id)



def create_connection(db_file=":memory:"):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
    return None

def save_match_data_sqlite(match_id, data):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO matches (match_id, data) VALUES (?, ?)",
                           (match_id, json.dumps(data)))
            conn.commit()
            return cursor.lastrowid, match_id
        except sqlite3.Error as e:
            print(f"Erro ao salvar dados no SQLite: {e}")
        finally:
            conn.close()
    return None, None


def save_match_data_sqlite(match_id, data):
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        match_id_int = int(match_id)
        cursor.execute("INSERT OR REPLACE INTO matches (match_id, data) VALUES (?, ?)",
                       (match_id_int, json.dumps(data)))
        conn.commit()
        return cursor.lastrowid, match_id_int
    except Exception as e:
        print(f"Erro ao salvar dados no SQLite: {e}")
        return None, None
    finally:
        conn.close()



def get_saved_match_data_sqlite(match_id):
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, match_id FROM matches WHERE match_id = ?", (int(match_id),))
        result = cursor.fetchone()
        if result:
            return {"_id": result[0], "match_id": int(result[1])}
        return None
    except Exception as e:
        print(f"Erro ao recuperar dados do SQLite: {e}")
        return None
    finally:
        conn.close()