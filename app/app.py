
import streamlit as st
import warnings
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.utils import get_competitions, get_matches, get_match_data
from src.utils.utils import save_match_data, get_saved_match_data
from src.database import collection


warnings.filterwarnings("ignore", category=UserWarning)

st.title("Análise de Partidas de Futebol")

# Verifica se o MongoDB está disponível
mongodb_available = collection is not None

if mongodb_available:
    default_db = "MongoDB"
else:
    #st.warning("MongoDB não está disponível. SQLite será usado como fallback.")
    default_db = "SQLite"

# Se o mongodb estiver disponível, cria o botão de rádio para seleção
if mongodb_available:
    db_choice = st.radio("Escolha o banco de dados:", ("MongoDB", "SQLite"), index=0 if default_db == "MongoDB" else 1)
else:
    db_choice = "SQLite"
    #st.info("Usando SQLite como única opção disponível.")

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
            else:
                st.error(f"Erro ao salvar os dados da partida no {db_choice}.")
        else:
            st.error("Não foi possível obter os dados da partida.")
    else:
        st.success("Dados recuperados com sucesso!")
        st.json({"_id": saved_data.get("_id"), "match_id": saved_data.get("match_id")})