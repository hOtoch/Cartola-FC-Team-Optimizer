import requests
import json
import pulp
import os
from dotenv import load_dotenv
from email_sender import Emailer
import schedule
from time import sleep

def otimizadorLPI(atletas_filter, budget, posicoes):

    prob = pulp.LpProblem("Melhor time do Cartola FC", pulp.LpMaximize)

    # Criando as variáveis de decisão onde 1 é se o jogador foi escolhido e 0 caso contrário
    player_vars = pulp.LpVariable.dicts("Player", [player['id'] for player in atletas_filter], 0, 1, pulp.LpInteger)

    # Função objetivo: maximizar a média dos jogadores escolhidos
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
        
    return selected_players_by_position, selected_players

def definir_conteudo(selected_players, selected_players_by_position, budget, capitao):
    resposta_email = f"<h2>Jogadores selecionados com o orçamento de {budget}:</h2><br>"

    for posicao, players in selected_players_by_position.items():
        resposta_email += f"<h3>{posicao}:</h3><ul>"
        for player in players:
            if player['id'] == capitao['atleta_id']:
                resposta_email += f"<li><strong>{player['apelido']} - Preço: {player['preco']} - Média: {player['media']} (CAPITÃO)</strong></li>"
            else:     
                resposta_email += f"<li>{player['apelido']} - Preço: {player['preco']} - Média: {player['media']}</li>"
        resposta_email += "</ul>"

    total_cost = sum(player['preco'] for player in selected_players)
    total_media = sum(player['media'] for player in selected_players)

    resposta_email += f"<br><strong>Custo total:</strong> {total_cost}<br>"
    resposta_email += f"<strong>Média total:</strong> {total_media}"
    
    return resposta_email
    
def enviar_email(resposta_email, num_rodada):
        
    # Enviar email com os jogadores selecionados
    email_sender = Emailer(os.environ.get('EMAIL_FROM'), os.environ.get('EMAIL_KEY'))

    email_sender.definir_conteudo(f"Melhor time do Cartola FC para a Rodada {num_rodada}", os.environ.get('EMAIL_FROM'), [os.environ.get('EMAIL_TO')], resposta_email, is_html=True)
    
    email_sender.enviar_email(60)
    
def job():
     # Atletas disponíveis no mercado do cartola
    url_status = "https://api.cartolafc.globo.com/mercado/status"
    resposta_status = requests.request("GET", url_status)
    status = json.loads(resposta_status.content)
    
    if status['status_mercado'] == 2:
        print("O mercado do Cartola FC está fechado")
        exit()
   
    
    url_atletas = "https://api.cartolafc.globo.com/atletas/mercado"
    resposta_atletas = requests.request("GET", url_atletas)
    objetos = json.loads(resposta_atletas.content)

    posicoes = {"1" : {"id": 1, "nome": "Goleiro","qtd" : 1},
                "2" : {"id": 2, "nome": "Lateral","qtd" : 2},
                "3" : {"id": 3, "nome": "Zagueiro","qtd" : 2},
                "4" : {"id": 4, "nome": "Meia","qtd" : 3},
                "5" : {"id": 5, "nome": "Atacante","qtd" : 3},
                "6" : {"id": 6, "nome": "Técnico","qtd" : 1}}

    budget = 110.0
    num_rodada = status['rodada_atual']
    atletas_filter = []
    
    load_dotenv()
    
    capitao = None
    mediaCapitao = 0

    for atleta in objetos['atletas']:
        if atleta['status_id'] == 7: # Se o jogador estiver disponível
            if atleta['media_num'] > mediaCapitao:
                capitao = atleta
                mediaCapitao = atleta['media_num']
            
            atletas_filter.append({
                'id' : atleta['atleta_id'],
                'apelido': atleta['apelido'],
                'posicao': posicoes[str(atleta['posicao_id'])]['nome'],
                'preco': atleta['preco_num'],
                'media': atleta['media_num'],
            })
        
    if not atletas_filter:
        print("O mercado do Cartola FC está fechado")
        exit()
    else:
        print("Otimizando time...")
        selected_players_by_position, selected_players = otimizadorLPI(atletas_filter, budget, posicoes)
        print("Time otimizado!\n\n")
        resposta = definir_conteudo(selected_players, selected_players_by_position, budget,capitao)
        
        try:
            enviar_email(resposta, num_rodada)
            print("Email enviado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            exit()
    
if __name__ == "__main__":
    print('Iniciando o script...')
    schedule.every(1).days.at("11:00").do(job)
    
    while True:
        schedule.run_pending()
        sleep(1)
    
    
   
