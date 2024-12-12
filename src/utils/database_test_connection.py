from pymongo import MongoClient
from urllib.parse import quote_plus

# Escape de caracteres especiais na senha
username = quote_plus("infnet-pbcda")
password = quote_plus("nathalialinhares290705")
host = "179.124.242.238"
port = "27017"
database = "admin"

# Construa a string de conexão
uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"

try:
    # Tente estabelecer uma conexão
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    
    # Tente uma operação simples para verificar a conexão
    client.admin.command('ping')
    
    print("Conexão bem-sucedida!")
    
    # Liste os bancos de dados disponíveis
    print("Bancos de dados disponíveis:")
    for db in client.list_database_names():
        print(f" - {db}")
    
except Exception as e:
    print(f"Erro ao conectar: {e}")

finally:
    # Sempre feche a conexão quando terminar
    if 'client' in locals():
        client.close()