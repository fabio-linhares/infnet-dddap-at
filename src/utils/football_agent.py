from langchain.agents import Tool, AgentExecutor, BaseSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain import LLMChain
from langchain.llms.base import LLM
from langchain.schema import AgentAction, AgentFinish
from typing import List, Union, Optional, Any, Tuple
from src.utils.utils import get_match_data
from src.utils.llm_utils import generate_llm_response
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Função para consultar eventos
def query_events(match_id: int, query: str) -> str:
    match_data = get_match_data(match_id)
    df = pd.DataFrame(match_data)
    
    try:
        result = df.query(query)
        return result[['minute', 'type', 'player', 'team', 'position']].to_json(orient='records')
    except Exception as e:
        return json.dumps({"error": f"Erro ao executar a consulta: {str(e)}"})

# Função para comparar jogadores
def compare_players(match_id: int, player1: str, player2: str) -> str:
    match_data = get_match_data(match_id)
    df = pd.DataFrame(match_data)
    
    player1_data = df[df['player'] == player1]
    player2_data = df[df['player'] == player2]

    comparison_data = {
        'Jogador': [player1, player2],
        'Total de Eventos': [len(player1_data), len(player2_data)],
        'Passes': [len(player1_data[player1_data['type'] == 'Pass']), len(player2_data[player2_data['type'] == 'Pass'])],
        'Chutes': [len(player1_data[player1_data['type'] == 'Shot']), len(player2_data[player2_data['type'] == 'Shot'])],
        'Faltas Cometidas': [len(player1_data[player1_data['type'] == 'Foul Committed']), len(player2_data[player2_data['type'] == 'Foul Committed'])]
    }

    comparison_df = pd.DataFrame(comparison_data)
    
    fig = go.Figure(data=[
        go.Bar(name=player1, x=comparison_df.columns[1:], y=comparison_df.iloc[0, 1:]),
        go.Bar(name=player2, x=comparison_df.columns[1:], y=comparison_df.iloc[1, 1:])
    ])
    fig.update_layout(barmode='group', title='Comparação entre Jogadores')
    
    return json.dumps({
        "comparison_data": comparison_df.to_dict(orient='records'),
        "plot": fig.to_json()
    })

# Função para obter estatísticas gerais da partida
def get_match_stats(match_id: int) -> str:
    match_data = get_match_data(match_id)
    df = pd.DataFrame(match_data)
    
    # Contagem de eventos por jogador
    player_events = df['player'].value_counts().reset_index()
    player_events.columns = ['Jogador', 'Número de Eventos']

    player_events_fig = px.bar(player_events, x='Jogador', y='Número de Eventos', title='Eventos por Jogador')

    # Gráfico de pizza para tipos de eventos
    event_types = df['type'].value_counts().reset_index()
    event_types.columns = ['Tipo de Evento', 'Contagem']

    event_types_fig = px.pie(event_types, values='Contagem', names='Tipo de Evento', title='Distribuição de Tipos de Eventos')

    return json.dumps({
        "player_events": player_events.to_dict(orient='records'),
        "player_events_plot": player_events_fig.to_json(),
        "event_types": event_types.to_dict(orient='records'),
        "event_types_plot": event_types_fig.to_json()
    })

# Classe CustomLLM compatível com LangChain
class CustomLLM(LLM):
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return generate_llm_response(prompt)

    @property
    def _llm_type(self) -> str:
        return "custom"

# Classe do prompt
class CustomPromptTemplate(StringPromptTemplate):
    template: str
    tools: List[Tool]
    
    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("intermediate_steps", "")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservação: {observation}\n"
        kwargs["agent_scratchpad"] = thoughts
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        return self.template.format(**kwargs)

# Classe do agente
class FootballAgent(BaseSingleActionAgent):
    llm_chain: LLMChain
    tools: List[Tool]
    
    def get_allowed_tools(self) -> List[str]:
        return [tool.name for tool in self.tools]

    @property
    def input_keys(self):
        return ["input"]

    def plan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any) -> Union[AgentAction, AgentFinish]:
        input_text = kwargs["input"]
        
        # Use a LLMChain para decidir a próxima ação
        full_inputs = {
            "input": input_text,
            "intermediate_steps": intermediate_steps,
            "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
        }
        output = self.llm_chain.predict(**full_inputs)
        
        if "Final Answer:" in output:
            return AgentFinish({"output": output.split("Final Answer:")[-1].strip()}, output)
        
        for tool in self.tools:
            if tool.name in output:
                tool_input = self.get_tool_input(output)
                return AgentAction(tool=tool.name, tool_input=tool_input, log=output)
        
        return AgentFinish({"output": output}, output)

    async def aplan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any) -> Union[AgentAction, AgentFinish]:
        return self.plan(intermediate_steps, **kwargs)

    def get_tool_input(self, output: str) -> str:
        return output.split("Tool Input:")[-1].strip()

# Template do prompt
template = """Você é um assistente de análise de futebol. Use as ferramentas disponíveis para responder às perguntas sobre a partida.

Ferramentas disponíveis:
{tools}

Pergunta do usuário: {input}

Pense passo a passo:
1) Qual ferramenta é mais adequada para responder à pergunta?
2) Que informações específicas você precisa extrair?
3) Como você pode formular a consulta ou comparação?

{agent_scratchpad}

Resposta:"""


def run_football_agent(match_id: int, query: str) -> str:
    # Definição das ferramentas
    tools = [
        Tool(
            name="Query Events",
            func=lambda x: query_events(match_id, x),
            description="Útil para consultar eventos específicos da partida. Use uma string de consulta pandas."
        ),
        Tool(
            name="Compare Players",
            func=lambda x: compare_players(match_id, *x.split(',')),
            description="Útil para comparar dois jogadores. Forneça os nomes dos jogadores separados por vírgula."
        ),
        Tool(
            name="Match Stats",
            func=lambda x: get_match_stats(match_id),
            description="Útil para obter estatísticas gerais da partida."
        )
    ]

    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        input_variables=["input", "intermediate_steps", "tools"]
    )

    llm = CustomLLM()
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    agent = FootballAgent(llm_chain=llm_chain, tools=tools)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

    return agent_executor.run(query)