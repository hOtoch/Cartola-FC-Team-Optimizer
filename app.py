import requests
import pandas as pd
import json
import pulp

# Atletas disponiveis no mercado do cartola
url = "https://api.cartolafc.globo.com/atletas/mercado"
resposta = requests.request("GET", url)
objetos = json.loads(resposta.content)

posicoes = {"1" : {"id": 1, "nome": "Goleiro","qtd" : 1},
            "2" : {"id": 2, "nome": "Lateral","qtd" : 2},
            "3" : {"id": 3, "nome": "Zagueiro","qtd" : 2},
            "4" : {"id": 4, "nome": "Meia","qtd" : 3},
            "5" : {"id": 5, "nome": "Atacante","qtd" : 3},
            "6" : {"id": 6, "nome": "Técnico","qtd" : 1}}

budget = 150.0

atletas_filter = []

for atleta in objetos['atletas']:
    if atleta['status_id'] == 7: # Se o jogador estiver disponível
        atletas_filter.append({
            'id' : atleta['atleta_id'],
            'apelido': atleta['apelido'],
            'posicao': posicoes[str(atleta['posicao_id'])]['nome'],
            'preco': atleta['preco_num'],
            'media': atleta['media_num'],
        })

prob = pulp.LpProblem("Melhor time do Cartola FC", pulp.LpMaximize)

# Criando as variaveis de decisão onde 1 é se o jogador foi escolhido e 0 caso contrário
player_vars = pulp.LpVariable.dicts("Player", [player['id'] for player in atletas_filter], 0, 1, pulp.LpInteger)

# Função objetivo : maximizar a média dos jogadores escolhidos
prob += pulp.lpSum([player['media'] * player_vars[player['id']] for player in atletas_filter]), "Total Cost"

# Restrição de orçamento
prob += pulp.lpSum([player['preco'] * player_vars[player['id']] for player in atletas_filter]) <= budget, "Budget"

# Restrições da quantidade de jogadores por posição
for posicao in posicoes.values():
    prob += pulp.lpSum([player_vars[player['id']] for player in atletas_filter if player['posicao'] == posicao['nome']]) == posicao['qtd'], f"{posicao['nome']} Count"


prob.solve()

selected_players = [player for player in atletas_filter if player_vars[player['id']].value() == 1]
selected_players_by_position = {pos['nome']: [] for pos in posicoes.values()}

for player in selected_players:
    selected_players_by_position[player['posicao']].append(player)

print("Jogadores selecionados:")
for posicao, players in selected_players_by_position.items():
    print(f"\n{posicao}:")
    for player in players:
        print(f"  {player['apelido']} - Preço: {player['preco']} - Média: {player['media']}")

total_cost = sum(player['preco'] for player in selected_players)
total_media = sum(player['media'] for player in selected_players)

print(f"\nCusto total: {total_cost}")
print(f"Média total: {total_media}")