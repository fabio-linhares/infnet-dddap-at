from fastapi import FastAPI, HTTPException
from src.utils.utils import get_match_data, save_match_data, get_saved_match_data

app = FastAPI()

@app.post("/match/{match_id}")
async def add_match_data(match_id: int):
    data = get_match_data(match_id)
    if not data:
        raise HTTPException(status_code=404, detail="Dados da partida não encontrados")
    
    inserted_id = save_match_data(match_id, data)
    if not inserted_id:
        raise HTTPException(status_code=500, detail="Erro ao salvar dados da partida")
    
    return {"message": "Dados da partida salvos com sucesso", "inserted_id": inserted_id}

@app.get("/match/{match_id}")
async def get_match_data_api(match_id: int):
    data = get_saved_match_data(match_id)
    if not data:
        raise HTTPException(status_code=404, detail="Dados da partida não encontrados")
    
    return data