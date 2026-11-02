import pandas as pd
import yaml 
import math
import json
from pathlib import Path

from functions import count_votes, treat_nominees, treat_nominees_no_limit
from image_generator import generate_image_nominees

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

csv_file = config['csv_path']
df = pd.read_csv(csv_file, sep=',', encoding='utf-8')

nominees = {}

dados = df.drop(columns=df.columns[[0,1,19,20,21]])
dados_duplas = df.iloc[:, 19:22]

div_number = config['div_number']

#Contando votos de todas as categorias exceto as de duplas
for column in dados:
    votes = {}
    for linha in dados[column]:
        linha = linha.split(", ")
        for nome in linha:
            count_votes(votes, nome)

    most_voted = max(votes.values())
    limit = math.trunc(most_voted/div_number)
    votes_in_order = dict(sorted(votes.items(), key=lambda d: d[1], reverse=True))

    nominees[column] = []
    for contender in votes_in_order:
        if votes_in_order[contender] >= limit:
            nominees[column].append([contender, votes_in_order[contender]])

    num = len(nominees[column])
    if num > 5:
        treat_nominees(column, nominees, 5)
    elif num < 3:
        nominees[column] = [
            [contender, total]
            for contender, total in votes_in_order.items()
        ]

        treat_nominees(column, nominees, 3)

#Contando votos da categoria de Duplas
votes = {}
for column in dados_duplas:
    for linha in dados_duplas[column]:
        if pd.notna(linha):
            count_votes(votes, linha)

votes_in_order = dict(sorted(votes.items(), key=lambda d: d[1], reverse=True))

duplas = "🏆 Prêmio Dupla do Ano"
nominees[duplas] = [
    [contender, total]
    for contender, total in votes_in_order.items()
]
treat_nominees(duplas, nominees, 3)

items = list(nominees.items())
items[-2], items[-1] = items[-1], items[-2]
nominees = dict(items)

path_config = Path(config['output_path'])
path = Path(path_config/'nominees.json')

generate_image_nominees(nominees, path_config)

with open(path, "w", encoding="utf-8") as file:
    json.dump(nominees, file, indent=4)