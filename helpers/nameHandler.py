
import json, datetime

path = "data/PeopleData.json"  # Essa path aqui é relativa e tá reescrita pra rodar pela main.py, mas no caso de rodar o arquivo sozinho, vai dar erro.
                               # Altere pra ../data/PeopleData.json pra rodar sozinho.
data : dict = {}  # Inicializa um dicionário vazio para armazenar os dados das pessoas. Coloquei aqui pois tem que ser acessado por esse with e a get_metadata.

with open(path) as file:  # Abre o arquivo de dados das pessoas.
    data = json.load(file)

def get_metadata(name) -> dict:
    """
    Retorna os metadados de uma pessoa com base no nome fornecido.

    Args:
        name (str): O nome da pessoa.

    Returns:
        dict: Um dicionário contendo os metadados da pessoa.
    """
    for person in data:
        if person['nome'] == name:
            return person

def get_welcome_string(metadata) -> str:
    """
    Retorna uma string de boas-vindas personalizada com base nos metadados fornecidos.

    Args:
        metadata (dict): Um dicionário contendo os metadados da pessoa.

    Returns:
        str: Uma string de boas-vindas personalizada.
    """
    if len(metadata["cargo"]) > 1:  # Cuida do honorífico e do cargo.
        cargo_string = f'{metadata["cargo"][0]} {metadata["cargo"][-1]}'
    else:  # Alguns não tem honorífico ou cargo, como estagiários.
        cargo_string = metadata["cargo"][0]

    if datetime.datetime.now().hour < 12:  # Caso seja de manhã, vai dizer bom dia.
        greeting = "Bom dia"
    elif datetime.datetime.now().hour < 18:  # Caso seja de tarde, vai dizer boa tarde.
        greeting = "Boa tarde"
    else:  # Caso seja de noite, vai dizer boa noite. Mas meio estranho, já que é pra ser uma saudação de chegada e não tem turno noturno.
        greeting = "Boa noite..."
        message = f'{greeting} {cargo_string} {metadata["nome"]}, o que faz aqui a esta hora?'

    message = f'{greeting} {cargo_string} {metadata["nome"]}.' # Monta a mensagem de boas-vindas. De acordo com a hora, nome, cargo e honorífico.

    return message
