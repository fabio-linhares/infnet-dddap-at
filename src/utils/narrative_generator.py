from src.utils.utils import get_match_data
from src.utils.llm_utils import generate_llm_response

def generate_match_narrative(match_id, style):
    match_data = get_match_data(match_id)
    
    if not match_data:
        return "Não foi possível obter os dados da partida."

    # Extrair informações relevantes da partida
    home_team = match_data[0]['team']
    away_team = [event['team'] for event in match_data if event['team'] != home_team][0]
    events = [event for event in match_data if event['type'] in ['Shot', 'Substitution', 'Foul Committed', 'Card']]

    # Criar um resumo básico dos eventos
    summary = f"Partida entre {home_team} e {away_team}.\n"
    for event in events:
        if event['type'] == 'Shot' and event.get('shot_outcome') == 'Goal':
            summary += f"Gol de {event['player']} para o {event['team']} no minuto {event['minute']}.\n"
        elif event['type'] == 'Card':
            summary += f"Cartão {event['card']['name']} para {event['player']} do {event['team']} no minuto {event['minute']}.\n"
        elif event['type'] == 'Substitution':
            summary += f"Substituição no {event['team']}: {event['player']} sai no minuto {event['minute']}.\n"
        elif event['type'] == 'Foul Committed':
            summary += f"Falta cometida por {event['player']} do {event['team']} no minuto {event['minute']}.\n"

    # Definir prompts para diferentes estilos de narração
    prompts = {
        'formal': f"""
        Crie uma narrativa formal e objetiva para a seguinte partida de futebol:
        
        {summary}
        
        Use uma linguagem técnica e profissional, focando nos fatos e estatísticas mais relevantes. Mantenha um tom imparcial e analítico ao descrever os eventos da partida.
        """,
        'humoristico': f"""
        Crie uma narrativa humorística e descontraída para a seguinte partida de futebol:
        
        {summary}
        
        Use um tom leve e bem-humorado, incluindo trocadilhos, analogias engraçadas e comentários espirituosos sobre os eventos da partida. Seja criativo e divertido, mas mantenha-se respeitoso com os times e jogadores.
        """,
        'tecnico': f"""
        Crie uma narrativa técnica e detalhada para a seguinte partida de futebol:
        
        {summary}
        
        Faça uma análise aprofundada dos eventos da partida, focando em aspectos táticos, técnicos e estratégicos. Discuta formações, padrões de jogo, e como eventos específicos impactaram o desenrolar da partida. Use termos técnicos do futebol e ofereça insights sobre as decisões dos treinadores e performances individuais dos jogadores.
        """
    }

    # Gerar a narrativa usando o LLM
    narrative = generate_llm_response(prompts[style])
    
    return narrative