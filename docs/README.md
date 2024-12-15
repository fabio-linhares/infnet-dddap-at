# Projeto: Desenvolvimento de Data-Driven Apps com Python

![Instituto Infnet](https://th.bing.com/th/id/OIP.IGWFD2IEXzA6njAKPpwCRwHaD4?rs=1&pid=ImgDetMain)

Este projeto foi desenvolvido como parte da disciplina **Desenvolvimento de Data-Driven Apps com Python [24E4_3]**, oferecida pelo [Instituto Infnet](https://ead.infnet.edu.br/faculdade/ciencia-de-dados-data-science/).

## Informações do Projeto

- **Autor**: Fábio Linhares  

---

## Sobre o Projeto

O projeto consiste no desenvolvimento de uma aplicação orientada a dados, utilizando as melhores práticas em Python para manipulação, análise e visualização de dados.

---

## Estrutura do Código

A aplicação está organizada nos seguintes diretórios principais:

- **`app`**: Código da aplicação principal.  
- **`data`**: Diretório com os dados utilizados no projeto.  
- **`docs`**: Contém documentação do projeto.  
- **`src`**: Código-fonte, dividido em módulos e utilitários.  
- **`tests`**: Testes automatizados para validação de funcionalidades.  

---

## Estrutura de Diretórios

```plaintext
.
├── LICENSE
├── app
│   ├── __init__py
│   └── app.py
├── data
│   ├── conhecimentos.csv
│   └── football_data.db
├── docs
│   └── README.md
├── environment.yml
├── main_fastapi.py
├── main_llm.py
├── requirements.txt
├── src
│   ├── api.py
│   ├── api_fastapi.py
│   ├── database.py
│   └── utils
│       ├── __init__.py
│       ├── database_test_connection.py
│       ├── llm_utils.py
│       ├── sqlite_utils.py
│       └── utils.py
└── tests
    ├── __init__.py
    └── test_utils.py

```
## Funcionalidades Implementadas

Esta implementação inicial estabelece a base para futuras análises mais detalhadas e visualizações dos dados das partidas de futebol.

### 1. Obtenção e Armazenamento de Dados de Partidas de Futebol

Nesta primeira fase do projeto, implementamos as seguintes funcionalidades:

#### Integração com StatsBomb API
- Utilizamos o pacote `statsbombpy` para acessar dados de partidas de futebol.
- Implementamos funções para obter informações sobre competições, temporadas e partidas específicas.

#### Armazenamento no MongoDB
- Criamos uma conexão com o MongoDB para armazenar os dados obtidos.
- Implementamos funções para salvar e recuperar dados de partidas no banco de dados.

#### Interface de Usuário com Streamlit
- Desenvolvemos uma interface interativa usando Streamlit.
- Os usuários podem selecionar competições, temporadas e partidas específicas.
- Um botão "Exibir Dados" permite aos usuários visualizar informações da partida selecionada.

#### Fluxo de Dados
1. **Obtenção de Dados**: 
   - Utilizamos a função `sb.events()` do `statsbombpy` para obter dados detalhados de uma partida específica.
2. **Processamento de Dados**: 
   - Convertemos tipos de dados NumPy para formatos compatíveis com MongoDB usando a função `convert_numpy_types()`.
3. **Armazenamento**: 
   - Salvamos os dados processados no MongoDB usando a função `save_match_data()`.
4. **Recuperação**: 
   - Recuperamos dados salvos do MongoDB usando a função `get_saved_match_data()`.

#### Rotas API Implementadas
Nossa aplicação expõe dois endpoints API principais para interagir com os dados das partidas:

- **GET**: Implementamos uma rota para recuperar dados de partidas salvas no MongoDB.
- **POST**: Criamos uma rota para salvar novos dados de partidas no MongoDB.

Estes endpoints fornecem uma interface programática para adicionar e recuperar dados de partidas, permitindo integração com outros sistemas ou scripts automatizados. Também adicionamos tratamento de Erros e Feedback para lidar com falhas na obtenção ou salvamento de dados através de mensagens de sucesso ou erro no Streamlit.


##### 1. Adicionar Dados da Partida

**Endpoint:** `POST /match/{match_id}`

Este endpoint permite adicionar dados de uma partida específica ao banco de dados.

```python
Rota:
@app.post("/match/{match_id}")

Parâmetros:
match_id (int): ID único da partida

Resposta de Sucesso:
Código: 200
Conteúdo: {"message": "Dados da partida salvos com sucesso", "inserted_id": "<id>"}

Respostas de Erro:
Código: 404 - Dados da partida não encontrados
Código: 500 - Erro ao salvar dados da partida
```

##### 2. Recuperar Dados da Partida

**Endpoint:** GET /match/{match_id}

Este endpoint permite recuperar os dados salvos de uma partida específica.

```python
Rota:
@app.get("/match/{match_id}")

Parâmetros:
match_id (int): ID único da partida

Resposta de Sucesso:
Código: 200
Conteúdo: Dados da partida em formato JSON

Resposta de Erro:
Código: 404 - Dados da partida não encontrados

```
---

## Requisitos do Ambiente

### Requisitos de Python

- Python 3.11 ou superior  

### Instalação com Conda

Para criar o ambiente utilizando o arquivo `environment.yml`, execute os comandos abaixo:

```bash
conda env create -f environment.yml
conda activate dddap_at2
```

### Instalação com pip

Caso prefira utilizar o `pip`, instale as dependências a partir do arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Configuração do Arquivo `.env`

Para garantir o funcionamento correto da aplicação, crie um arquivo `.env` na raiz do projeto com as seguintes chaves:

- `MONGODB_USER`: Nome de usuário para o MongoDB.  
- `MONGODB_PASSWORD`: Senha correspondente ao usuário.  
- `MONGODB_HOST`: Endereço do host onde o MongoDB está hospedado.  
- `MONGODB_PORT`: Porta utilizada pelo MongoDB.  
- `MONGODB_DATABASE`: Nome do banco de dados de administração.  
- `MONGODB_MAIN_DB`: Nome do banco de dados principal utilizado na aplicação.  
- `MONGODB_USER_COLLECTION`: Nome da coleção usada para armazenar dados de partidas.  

---

## Como Executar

1. Certifique-se de que o ambiente está ativado.  
2. Navegue até o diretório principal do projeto.  
3. Execute o arquivo principal:

```bash
python main.py
```

---

## Dependências Principais

- **Altair**: Biblioteca para visualização de dados.  
- **Pandas**: Manipulação e análise de dados.  
- **Numpy**: Operações matemáticas e array.  
- **Streamlit**: Criação de aplicativos web interativos para dados.  
- **StatsBombPy**: Coleta de dados esportivos.  

---

## Contato

- **Aluno**: Fábio Linhares  
- **Professor**: Fernando Guimarães Ferreira [github.com/fernandoferreira-me](https://github.com/fernandoferreira-me)
- **Instituição**: Instituto Infnet  
- **E-mail**: [fabio.linhares@infnet.edu.br](mailto:fabio.linhares@infnet.edu.br)  
- **LinkedIn**: [linkedin.com/in/fabio-linhares](https://www.linkedin.com/in/fabio-linhares/)  
- **GitHub**: [github.com/fabio-linhares](https://github.com/fabio-linhares), [github.com/zerodevsystem](https://github.com/zerodevsystem)  

---

## Licença

Este projeto está sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.  

