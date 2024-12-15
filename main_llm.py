import uvicorn
from dotenv import load_dotenv
import os

# Obtém o caminho absoluto para o diretório do projeto
project_dir = os.path.dirname(os.path.abspath(__file__))

# Carrega as variáveis de ambiente
load_dotenv(os.path.join(project_dir, '.env'))

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)






