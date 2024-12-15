import json
import ast
import numpy as np
import pandas as pd
import datetime
from bson import json_util
from statsbombpy import sb
from src.database import collection, get_sqlite_connection
from pymongo import ReturnDocument
import sqlite3
from src.utils.llm_utils import generate_llm_response
from src.database import get_db_connection, is_mongodb_available


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
    if collection is not None:
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
    if collection is not None: 
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
####################


def get_match_summary(match_id):
    saved_resumo = get_saved_resumo(convert_numpy_types(match_id))
    if saved_resumo:
        return saved_resumo

    match_data = get_match_data(match_id)
    if match_data:
        # Identificar times
        home_team = match_data[0]['team']
        away_team = match_data[1]['team']

        # Inicializar contadores e listas
        home_goals = []
        away_goals = []
        home_fouls = 0
        away_fouls = 0
        home_corners = 0
        away_corners = 0
        home_saves = 0
        away_saves = 0
        home_lineup = []
        away_lineup = []

        # Coletar detalhes dos eventos
        for event in match_data:
            if event['type'] == 'Shot' and event['shot_outcome'] == 'Goal':
                if event['team'] == home_team:
                    home_goals.append(event['player'])
                else:
                    away_goals.append(event['player'])

            if event['type'] == 'Foul Committed':
                if event['team'] == home_team:
                    home_fouls += 1
                else:
                    away_fouls += 1

            if event['type'] == 'Corner Taken':
                if event['team'] == home_team:
                    home_corners += 1
                else:
                    away_corners += 1

            if event['type'] == 'Save':
                if event['team'] == home_team:
                    home_saves += 1
                else:
                    away_saves += 1

            if event['type'] == 'Starting XI':
                if event['team'] == home_team:
                    home_lineup = [player['player']['name'] for player in event['tactics']['lineup']]
                else:
                    away_lineup = [player['player']['name'] for player in event['tactics']['lineup']]

        # Criar o resumo
        summary = (
            f"Match between {home_team} and {away_team}.\n"
            f"Final score: {home_team} {len(home_goals)} x {len(away_goals)} {away_team}.\n"
            f"Goals by {home_team}: {', '.join(home_goals)}.\n"
            f"Goals by {away_team}: {', '.join(away_goals)}.\n"
            f"Fouls committed: {home_team} {home_fouls}, {away_team} {away_fouls}.\n"
            f"Corners: {home_team} {home_corners}, {away_team} {away_corners}.\n"
            f"Saves: {home_team} {home_saves}, {away_team} {away_saves}.\n"
            f"Lineups:\n{home_team}: {', '.join(home_lineup)}\n{away_team}: {', '.join(away_lineup)}\n"
        )

        # Prompt para gerar o resumo completo
        prompt = f"""
        Summarize the following football match in Portuguese (Brazilian):
        
        Summary: {summary}

        Escreva um resumo detalhado da partida no formato de texto narrativo, destacando os seguintes pontos:
        1. Desfecho da partida (quem venceu ou se foi empate).
        2. Principais eventos, como gols, assistências, e jogadores que se destacaram.
        3. Informações estatísticas, incluindo:
        - Percentuais de posse de bola
        - Total de chutes e chutes no alvo
        - Defesas notáveis dos goleiros
        - Faltas cometidas por cada equipe
        4. Decisões táticas, substituições ou mudanças de formação, se relevantes.

        Por favor, escreva no estilo narrativo fluido, por exemplo: "O time A venceu o time B por 3 a 1. Os destaques foram os gols de João e Lucas, além de uma assistência de Ana. O time A teve 60% de posse de bola, contra 40% do time B..."
        """

        # Gerar o resumo final com o LLM
        summary_text = generate_llm_response(prompt)

        # return summary_text
        save_resumo(convert_numpy_types(match_id), convert_numpy_types(summary_text))
        return summary_text

    return None

def get_player_profile(match_id, player_id):
    saved_perfil = get_saved_perfil(convert_numpy_types(match_id), convert_numpy_types(player_id))
    if saved_perfil:
        return saved_perfil
    # Obter dados da partida e as escalações
    match_data = get_match_data(match_id)
    lineups = sb.lineups(match_id=match_id)

    if match_data and lineups:
        player_info = None
        player_team = None

        # Procurar informações do jogador nas escalações
        for team, lineup in lineups.items():
            player = lineup[lineup['player_id'] == int(player_id)]
            if not player.empty:
                player_info = player.iloc[0]
                player_team = team
                break

        if player_info is None:
            return "Jogador não encontrado nas escalações."

        def safe_get(value):
            return str(value) if pd.notna(value) else "N/A"

        player_name = safe_get(player_info.get("player_name"))
        player_nickname = safe_get(player_info.get("player_nickname"))
        jersey_number = safe_get(player_info.get("jersey_number"))
        birth_date = safe_get(player_info.get("birth_date"))
        country = safe_get(player_info.get("country"))
        gender = safe_get(player_info.get("player_gender"))
        height = safe_get(player_info.get("player_height"))
        weight = safe_get(player_info.get("player_weight"))

        # Criar o perfil inicial do jogador
        profile = f"Perfil de {player_name} ({player_team}):\n"
        profile += f"Apelido: {player_nickname}\n"
        profile += f"Número da camisa: {jersey_number}\n"
        profile += f"Data de Nascimento: {birth_date}\n"
        profile += f"País: {country}\n"
        profile += f"Gênero: {gender}\n"
        profile += f"Altura: {height} cm\n"
        profile += f"Peso: {weight} kg\n"

        # Filtrar eventos do jogador nos dados da partida
        player_events = [event for event in match_data if event.get('player') == player_name]

        if player_events:
            # Estatísticas básicas
            passes = sum(1 for event in player_events if event.get("type") == "Pass")
            successful_passes = sum(
                1
                for event in player_events
                if event.get("type") == "Pass" and not event.get("pass_outcome")
            )
            shots = sum(1 for event in player_events if event.get("type") == "Shot")
            goals = sum(
                1 for event in player_events if event.get("type") == "Shot" and event.get("shot_outcome") == "Goal"
            )
            assists = sum(
                1 for event in player_events if event.get("type") == "Pass" and event.get("pass_goal_assist")
            )
            tackles = sum(
                1 for event in player_events if event.get("type") == "Duel" and event.get("duel_type") == "Tackle"
            )

            # Estatísticas adicionais
            finalizacoes = shots
            minutos_jogados = max(event.get("minute", 0) for event in player_events)
            player_position = player_events[0].get("position", "Posição não especificada")

            # Atualizar o perfil com estatísticas
            profile += f"\nPosição: {player_position}\n"
            profile += f"\nEstatísticas da partida:\n"
            profile += f"Minutos jogados: {minutos_jogados}\n"
            profile += f"Passes: {passes} (Bem-sucedidos: {successful_passes})\n"
            profile += f"Finalizações: {finalizacoes}\n"
            profile += f"Gols: {goals}\n"
            profile += f"Assistências: {assists}\n"
            profile += f"Desarmes: {tackles}\n"

            # Preparar o prompt para gerar uma descrição mais narrativa do perfil
            prompt = f"""
            Crie um perfil detalhado do seguinte jogador de futebol em português (Brasil):

            Perfil: {profile}

            Como se fosse um comentarista da ESPN ou dos grandes canais de esporte do mundo, e te perguntassem sobre esse jogador,
            escreva o perfil narrativo dele utilizando os dados acima. Inclua os seguintes pontos:
            1. Se possível, apresente informações pessoais e contextuais (nome, posição, time, número da camisa, data de nascimento, país, gênero, altura e peso).
            2. Destaques do desempenho na partida, como o número de passes realizados (e bem-sucedidos), chutes, gols, assistências e desarmes.
            3. Comente brevemente sobre como essas estatísticas refletem o impacto do jogador na partida ou sua importância para o time.

            Por favor, escreva no estilo narrativo fluido, por exemplo: "João Silva, jogador do Time A, destacou-se na posição de atacante durante a partida. 
            Com 1,85 m de altura e 80 kg, ele demonstrou agilidade e precisão ao marcar dois gols e realizar uma assistência decisiva.
            Seus 30 passes, sendo 25 bem-sucedidos, evidenciaram sua habilidade em manter a posse de bola e criar jogadas importantes..."

            Foque nas informações que dispõe e deixe de lado as que não tem.
            """

            # Gerar o perfil detalhado através de uma LLM (como GPT)
            profile_text = generate_llm_response(prompt)

            save_perfil(convert_numpy_types(match_id), convert_numpy_types(player_id), convert_numpy_types(profile_text))
            return profile_text

        else:
            profile += "\nNenhum evento encontrado para o jogador nesta partida."

        return profile

    return "Não foi possível carregar os dados da partida ou das escalações."


def extract_player_data(match_data, player_id):
    #mais adiante...
    pass





def save_resumo(match_id, resumo):
    db = get_db_connection()
    if db['type'] == 'mongodb':
        try:
            result = db['resumos'].update_one(
                {"match_id": convert_numpy_types(match_id)},
                {"$set": {"resumo": convert_numpy_types(resumo)}},
                upsert=True
            )
            return result.upserted_id or result.modified_count > 0
        except Exception as e:
            print(f"Erro ao salvar resumo no MongoDB: {e}")
    else:
        conn = db['connection']()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO resumos (match_id, resumo) VALUES (?, ?)",
                           (match_id, resumo))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao salvar resumo no SQLite: {e}")
        finally:
            conn.close()

def get_saved_resumo(match_id):
    db = get_db_connection()
    if db['type'] == 'mongodb':
        result = db['resumos'].find_one({"match_id": convert_numpy_types(match_id)})
        if result:
            return convert_numpy_types(result.get("resumo"))
    else:
        conn = db['connection']()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT resumo FROM resumos WHERE match_id = ?", (match_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
        except Exception as e:
            print(f"Erro ao recuperar resumo do SQLite: {e}")
        finally:
            conn.close()
    
    return None


def save_perfil(match_id, player_id, perfil):
    db = get_db_connection()
    if db['type'] == 'mongodb':
        try:
            result = db['perfis'].update_one(
                {"match_id": convert_numpy_types(match_id), "player_id": convert_numpy_types(player_id)},
                {"$set": {"perfil": convert_numpy_types(perfil)}},
                upsert=True
            )
            return result.upserted_id or result.modified_count > 0
        except Exception as e:
            print(f"Erro ao salvar perfil no MongoDB: {e}")
    else:
        conn = db['connection']()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO perfis (match_id, player_id, perfil) VALUES (?, ?, ?)",
                           (match_id, player_id, perfil))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao salvar perfil no SQLite: {e}")
        finally:
            conn.close()

def get_saved_perfil(match_id, player_id):
    db = get_db_connection()
    if db['type'] == 'mongodb':
        result = db['perfis'].find_one({
            "match_id": convert_numpy_types(match_id),
            "player_id": convert_numpy_types(player_id)
        })
        if result:
            return convert_numpy_types(result.get("perfil"))
    else:
        conn = db['connection']()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT perfil FROM perfis WHERE match_id = ? AND player_id = ?", (match_id, player_id))
            result = cursor.fetchone()
            if result:
                return result[0]
        except Exception as e:
            print(f"Erro ao recuperar perfil do SQLite: {e}")
        finally:
            conn.close()
    
    return None