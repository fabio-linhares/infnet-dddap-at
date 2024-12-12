import os
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import quote_plus

def get_env_variable(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"A variável de ambiente {var_name} não está definida.")
    return value

def create_mongodb_client():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()

    # Obtém as variáveis de ambiente
    mongodb_user = get_env_variable('MONGODB_USER')
    mongodb_password = get_env_variable('MONGODB_PASSWORD')
    mongodb_host = get_env_variable('MONGODB_HOST')
    mongodb_port = get_env_variable('MONGODB_PORT')
    mongodb_database = get_env_variable('MONGODB_DATABASE')

    # Constrói a URI do MongoDB com escape adequado para usuário e senha
    mongodb_uri = f"mongodb://{quote_plus(mongodb_user)}:{quote_plus(mongodb_password)}@{mongodb_host}:{mongodb_port}/{mongodb_database}"

    try:
        client = MongoClient(mongodb_uri)
        # Tenta uma operação simples para verificar a conexão
        client.admin.command('ping')
        return client
    except Exception as e:
        raise ConnectionError(f"Erro ao conectar ao MongoDB: {e}")

def get_database_collection():
    client = create_mongodb_client()
    db_name = get_env_variable('MONGODB_MAIN_DB')
    collection_name = get_env_variable('MONGODB_USER_COLLECTION')
    return client[db_name][collection_name]

# Inicializa a conexão e obtém a coleção
collection = get_database_collection()