import streamlit as st
import warnings
import numpy as np
import sys
import os
from statsbombpy import sb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.utils import get_competitions, get_matches, get_match_data
from src.utils.utils import save_match_data, get_saved_match_data
from src.database import collection
from src.utils.utils import get_match_summary, get_player_profile

warnings.filterwarnings("ignore", category=UserWarning)

st.title("Análise de Partidas de Futebol")

# Inicialização do session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'match_summary' not in st.session_state:
    st.session_state.match_summary = ""
if 'player_profile' not in st.session_state:
    st.session_state.player_profile = ""
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = None
if 'players' not in st.session_state:
    st.session_state.players = {}

# Verifica se o MongoDB está disponível
mongodb_available = collection is not None

if mongodb_available:
    default_db = "MongoDB"
else:
    default_db = "SQLite"

# Se o mongodb estiver disponível, cria o botão de rádio para seleção
if mongodb_available:
    db_choice = st.radio("Escolha o banco de dados:", ("Online", "Local"), index=0 if default_db == "MongoDB" else 1)
else:
    db_choice = "SQLite"
    st.info("Usando SQLite como única opção disponível.")

# Exibe a escolha 
st.write(f"Banco de dados selecionado: {db_choice}")

# retorna um dataframe: https://github.com/statsbomb/statsbombpy/blob/master/README.md
competitions = get_competitions()

# Filtro de competição
competition_names = competitions['competition_name'].unique()
selected_competition = st.selectbox("Selecione a competição:", competition_names)

# Filtro de temporada
seasons = competitions[competitions['competition_name'] == selected_competition]['season_name'].unique()
selected_season = st.selectbox("Selecione a temporada:", seasons)

# Obter IDs de competição e temporada
competition_id = competitions[(competitions['competition_name'] == selected_competition) & 
                              (competitions['season_name'] == selected_season)]['competition_id'].iloc[0]
season_id = competitions[(competitions['competition_name'] == selected_competition) & 
                         (competitions['season_name'] == selected_season)]['season_id'].iloc[0]

# Carregar partidas
matches = get_matches(competition_id, season_id)

# Filtro de partida
match_names = [f"{row['home_team']} vs {row['away_team']} ({row['match_date']})" for _, row in matches.iterrows()]
selected_match = st.selectbox("Selecione a partida:", match_names)

if st.button("Exibir Dados"):
    selected_match_id = matches.iloc[match_names.index(selected_match)]['match_id']
    
    saved_data = get_saved_match_data(selected_match_id)
    
    if not saved_data:
        st.info("Dados não encontrados. Obtendo e salvando dados...")
        data = get_match_data(selected_match_id)
        if data:
            result = save_match_data(selected_match_id, data)
            if result:
                inserted_id, match_id_int = result
                st.success(f"Dados da partida salvos com sucesso no {db_choice}.")
                st.json({"_id": inserted_id, "match_id": match_id_int})
                st.session_state.data_loaded = True
                st.session_state.selected_match_id = selected_match_id
            else:
                st.error(f"Erro ao salvar os dados da partida no {db_choice}.")
        else:
            st.error("Não foi possível obter os dados da partida.")
    else:
        st.success("Dados recuperados com sucesso!")
        st.json({"_id": saved_data.get("_id"), "match_id": saved_data.get("match_id")})
        st.session_state.data_loaded = True
        st.session_state.selected_match_id = selected_match_id
    
    lineups = sb.lineups(match_id=st.session_state.selected_match_id)
    st.session_state.players = {}
    st.session_state.team_names = list(lineups.keys())

    for team, lineup in lineups.items():
        st.session_state.players[team] = []
        for _, player in lineup.iterrows():  
            st.session_state.players[team].append(f"{player['player_name']} ({player['player_id']})")

if st.session_state.get('data_loaded', False):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Gerar Resumo da Partida"):
            st.session_state.match_summary = get_match_summary(st.session_state.selected_match_id)
        
        if st.session_state.match_summary:
            st.subheader("Resumo da Partida")
            st.write(st.session_state.match_summary)
    
    with col2:
        st.session_state.selected_team = st.radio("Selecione o time:", st.session_state.team_names)
        
        # Modificar a estrutura de dados para armazenar nome e ID separadamente
        if 'players_data' not in st.session_state:
            st.session_state.players_data = {}
            for team, players in st.session_state.players.items():
                st.session_state.players_data[team] = [
                    {"name": player.split('(')[0].strip(), "id": player.split('(')[-1].split(')')[0]}
                    for player in players
                ]
        
        # Criar lista apenas com os nomes dos jogadores para o dropdown
        player_names = [player["name"] for player in st.session_state.players_data.get(st.session_state.selected_team, [])]
        
        selected_player_name = st.selectbox("Selecione o jogador:", player_names)
        
        if st.button("Gerar Perfil do Jogador"):
            # Encontrar o ID do jogador selecionado
            selected_player_data = next(
                (player for player in st.session_state.players_data[st.session_state.selected_team] 
                if player["name"] == selected_player_name),
                None
            )
            if selected_player_data:
                player_id = selected_player_data["id"]
                st.session_state.player_profile = get_player_profile(st.session_state.selected_match_id, player_id)
            else:
                st.error("Não foi possível encontrar o ID do jogador selecionado.")
        
        if st.session_state.player_profile:
            st.subheader("Perfil do Jogador")
            st.write(st.session_state.player_profile)
