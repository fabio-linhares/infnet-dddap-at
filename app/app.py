
import streamlit as st
import warnings
import numpy as np

from src.utils.utils import get_competitions, get_matches, get_match_data, save_match_data, get_saved_match_data

warnings.filterwarnings("ignore", category=UserWarning)

st.title("Análise de Partidas de Futebol")

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

# Botão Exibir Dados
if st.button("Exibir Dados"):
    selected_match_id = matches.iloc[match_names.index(selected_match)]['match_id']
    saved_data = get_saved_match_data(selected_match_id)
    
    if not saved_data:
        st.info("Dados não encontrados. Obtendo e salvando dados...")
        data = get_match_data(selected_match_id)
        if data:
            inserted_id, match_id_int = save_match_data(selected_match_id, data)
            if inserted_id:
                st.success("Dados da partida salvos com sucesso.")
                st.json({"_id": inserted_id, "match_id": match_id_int})
            else:
                st.error("Erro ao salvar os dados da partida no banco de dados.")
        else:
            st.error("Não foi possível obter os dados da partida.")
    else:
        st.success("Dados recuperados com sucesso!")
        st.json({"_id": saved_data.get("_id"), "match_id": saved_data.get("match_id")})
