# Projeto: Desenvolvimento de Data-Driven Apps com Python

Este projeto foi desenvolvido como parte da disciplina **Desenvolvimento de Data-Driven Apps com Python [24E4_3]**, oferecida pelo Instituto Infnet.

## Informações do Projeto

- **Aluno**: Fábio Linhares
- **Professor**: Fernando Guimarães
- **Disciplina**: Desenvolvimento de Data-Driven Apps com Python [24E4_3]

---

## Sobre o Projeto

O projeto consiste no desenvolvimento de uma aplicação orientada a dados, utilizando as melhores práticas em Python para manipulação, análise e visualização de dados.

## Estrutura de Diretórios

```plaintext
.
├── app
│   ├── __init__py
│   └── app.py
├── chat
├── data
│   └── conhecimentos.csv
├── docs
│   └── README.md
├── environment.yml
├── main.py
├── requirements.txt
├── src
│   ├── api.py
│   ├── database.py
│   └── utils
│       ├── __init__.py
│       ├── database_test_connection.py
│       └── utils.py
└── tests
    ├── __init__.py
    └── test_utils.py

9 directories, 19 files
```

## Requisitos do Ambiente

Certifique-se de instalar todas as dependências do projeto. Elas estão listadas nos arquivos `environment.yml` e `requirements.txt`.

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

## Dependências Principais

- **Altair**: Biblioteca para visualização de dados.
- **Pandas**: Manipulação e análise de dados.
- **Numpy**: Operações matemáticas e array.
- **Streamlit**: Criação de aplicativos web interativos para dados.
- **StatsBombPy**: Coleta de dados esportivos.

## Configuração do Arquivo `.env`

Para garantir o funcionamento correto da aplicação, é necessário criar um arquivo `.env` na raiz do projeto contendo as seguintes chaves de configuração:

- `MONGODB_USER`: Nome de usuário para acessar o banco de dados MongoDB.
- `MONGODB_PASSWORD`: Senha correspondente ao usuário.
- `MONGODB_HOST`: Endereço do host onde o MongoDB está hospedado.
- `MONGODB_PORT`: Porta utilizada pelo MongoDB.
- `MONGODB_DATABASE`: Nome do banco de dados de administração.
- `MONGODB_MAIN_DB`: Nome do banco de dados principal utilizado na aplicação.
- `MONGODB_USER_COLLECTION`: Nome da coleção utilizada para armazenar os dados de partidas do StatsBomb.

## Como Executar

1. Certifique-se de que o ambiente está ativado.
2. Navegue até o diretório principal do projeto.
3. Execute o arquivo principal:

```bash
python main.py
```

## Estrutura do Código

- **app**: Contém o código relacionado à aplicação principal.
- **data**: Diretório com os dados utilizados no projeto.
- **docs**: Documentação do projeto.
- **src**: Código-fonte, dividido em módulos e utilitários.
- **tests**: Testes automatizados para validação de funcionalidades.

---

## Autor e Contato

- **Aluno**: Fábio Linhares
- **Professor**: Fernando Guimarães
- **Disciplina**: Desenvolvimento de Data-Driven Apps com Python [24E4_3]
- **Instituição**: Instituto Infnet
- **E-mail**: fabio.linhares@infnet.edu.br

---

## Licença
Este projeto está sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.


