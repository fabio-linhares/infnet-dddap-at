from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.utils.utils import get_match_summary, get_player_profile
from src.database import get_sqlite_connection

app = FastAPI()

class MatchSummaryRequest(BaseModel):
    match_id: int

class MatchSummaryResponse(BaseModel):
    summary: str

class PlayerProfileRequest(BaseModel):
    match_id: int
    player_id: int

class PlayerProfileResponse(BaseModel):
    profile: str

@app.post("/match_summary", response_model=MatchSummaryResponse)
async def get_match_summary_api(request: MatchSummaryRequest):
    summary = get_match_summary(request.match_id)
    if summary:
        return MatchSummaryResponse(summary=summary)
    else:
        raise HTTPException(status_code=404, detail="Match summary not found")

@app.post("/player_profile", response_model=PlayerProfileResponse)
async def get_player_profile_api(request: PlayerProfileRequest):
    profile = get_player_profile(request.match_id, request.player_id)
    if profile:
        return PlayerProfileResponse(profile=profile)
    else:
        raise HTTPException(status_code=404, detail="Player profile not found")

# Função auxiliar para verificar a conexão com o banco de dados
@app.get("/health")
async def health_check():
    try:
        conn = get_sqlite_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")