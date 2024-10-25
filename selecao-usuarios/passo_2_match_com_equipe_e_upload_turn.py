### Match com equipe e Upload na Turn
# A partir dos usuários selecionados para o dia no Passo 1, une suas informações com suas informações 
# de equipe/estabelecimentos que esta no Big Query e advem da Turn. Após isso da upload desses contatos na turn.


#### Configurações iniciais do ambiente
import pandas as pd
import io
import numpy as np
from sklearn.model_selection import train_test_split
from google.oauth2 import service_account
from datetime import datetime
from google.cloud import bigquery
import requests
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()
credentials = service_account.Credentials.from_service_account_file('credencial_bigquery.json')
project_id = 'predictive-keep-314223'
client = bigquery.Client(credentials= credentials,project=project_id)



#### Funcoes
def get_token(municipio_id_sus):
    for token_info in tokens_municipios:
        if token_info['id_sus'] == municipio_id_sus:
            return token_info['token']
    return None

def send_data(df, municipio_id_sus):
    token = get_token(municipio_id_sus)
    if not token:
        print(f"Token não encontrado para {municipio_id_sus}")
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.v1+json',
        'Content-Type': 'application/json'
    }

    df_filtered = df[df['municipio_id_sus'] == municipio_id_sus]

    for i, row in df_filtered.iterrows():
        data_message = {
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(row.celular_tratado),
            "type": "text",
            "text": {"body": "Este número pertence a ImpulsoGov."}
        }
        url_message = 'https://whatsapp.turn.io/v1/messages'

        try:
            response_message = requests.post(url_message, headers=headers, json=data_message)
            print(f"Resposta da mensagem para {row.celular_tratado}: {response_message.text}")
        except Exception as e:
            print(f"Erro ao enviar mensagem para {row.celular_tratado}: {e}")
            continue

        time.sleep(1)

        #atualiza opted_in
        json_data_profile = {
            "opted_in": True,
        }
        url_profile = f'https://whatsapp.turn.io/v1/contacts/{row.celular_tratado}/profile'

        try:
            response_profile = requests.patch(url_profile, headers=headers, json=json_data_profile)
            print(f"Resposta do perfil para {row.celular_tratado}: {response_profile.text}")
        except Exception as e:
            print(f"Erro ao atualizar perfil de {row.celular_tratado}: {e}")

        time.sleep(1)



#### Consulta dos dados
query = """
    SELECT *
    FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens_teste`
"""

query_job = client.query(query)
rows = [dict(row) for row in query_job]
df_historico_envio_mensagens = pd.DataFrame(rows)
# carregando dados dos municipios da tabela do ibge
query = """
    SELECT *
    FROM `predictive-keep-314223.lista_de_codigos.municipios_ibge`
"""

query_job = client.query(query)
rows = [dict(row) for row in query_job]
df_ibge = pd.DataFrame(rows)
# carregando a view com dados da Turn io
query = """
    SELECT *
    FROM `predictive-keep-314223.ip_mensageria_camada_prata.contact_details_turnio`
"""

query_job = client.query(query)
rows = [dict(row) for row in query_job]
df_contatos_turnio = pd.DataFrame(rows)


#### Match
# Une dados da tabela de seção diaria "ip_mensageria_camada_prata.historico_envio_mensagens" do BigQuery 
# com os dados do estabelecimento que a pessoa é pertencente, por meio do dos dados que estão registradas 
# na view "ip_mensageria_camada_prata.contact_details_turnio" no BigQuery.
df_ibge['id_sus'] = df_ibge['id_sus'].astype(str)
df_historico_envio_mensagens['municipio_id_sus'] = df_historico_envio_mensagens['municipio_id_sus'].astype(str)
# merge da tabela de usuários com de municípios
df_historico_envio_mensagens = pd.merge(df_historico_envio_mensagens, df_ibge[['id_sus','nome','uf_sigla']], left_on=['municipio_id_sus'],right_on=['id_sus'] , how='left')
df_contatos_turnio[['municipio', 'uf']] = df_contatos_turnio['details_municipio'].str.split(' - ', expand=True)
# equipes com preencimento dos dados
df_contatos_turnio_preenchido = df_contatos_turnio[df_contatos_turnio['details_equipe_nome'].notnull()]
df_contatos_turnio_preenchido = df_contatos_turnio_preenchido[['details_equipe_nome','municipio','uf']].drop_duplicates().reset_index(drop=True)
# merge das tabelas de dados dos usuários e estabelecimento
df = pd.merge(df_historico_envio_mensagens, df_contatos_turnio, left_on=['equipe_nome','municipio','uf_sigla'], right_on=['details_equipe_nome','municipio','uf'], how='left')
df_envio_turn = df[['municipio',
                    'uf_sigla',
                    'municipio_id_sus',
                    'equipe_ine',
                    'equipe_nome',
                    'linha_cuidado',
                    'nome_do_paciente',
                    'data_de_nascimento',
                    'celular_tratado',
                    'mvp_tipo_grupo',
                    'mvp_data_envio',
                    'mvp_grupo',
                    'details_horarios_cronicos',
                    'details_telefone',
                    'details_estabelecimento_endereco',
                    'details_estabelecimento_telefone',
                    'details_estabelecimento_nome',
                    'details_horarios_cito',
                    'details_estabelecimento_documentos',
                    'details_estabelecimento_horario'
                    ]]

df_envio_turn = df_envio_turn.rename(columns={'details_horarios_cronicos':'horarios_cronicos',
                                              'details_telefone':'telefone',
                                              'details_estabelecimento_endereco':'estabelecimento_endereco',
                                              'details_estabelecimento_telefone':'estabelecimento_telefone',
                                              'details_estabelecimento_nome':'estabelecimento_nome',
                                              'details_horarios_cito':'horarios_cito',
                                              'details_estabelecimento_documentos':'estabelecimento_documentos',
                                              'details_estabelecimento_horario':'estabelecimento_horario'})
df_envio_turn[['municipio_id_sus','municipio']].drop_duplicates()




# #### Upload
# Da upload no perfil respectivo ao seu municipio na Turn. Inclui os seguintes campos:
# - opted_in=true
# - nome_do_paciente
# - linha_de_cuidado
# - municipio
# - municipio_id_sus
# - equipe_ine
# - equipe_nome
# - mvp_tipo_grupo
# - mvp_data_envio
# - mvp_grupo
# - estabelecimento_horario
# - estabelecimento_documentos
# - estabelecimento_nome
# - estabelecimento_endereco
# - estabelecimento_telefone
# - horarios_cronicos
# - horarios_cito
tokens_municipios = [
    {"municipio": "Paulo Ramos", "id_sus": "210810", "token": os.getenv('ENV_PAULORAMOS_MA')},
    {"municipio": "Lago Verde", "id_sus": "210590", "token": os.getenv('ENV_LAGOVERDE_MA')},
    {"municipio": "Pacoti", "id_sus": "230980", "token": os.getenv('ENV_PACOTI_CE')},
    {"municipio": "Monsenhor Tabosa", "id_sus": "230860", "token": os.getenv('ENV_MONSENHORTABOSA_CE')},
    {"municipio": "Marajá do Sena", "id_sus": "210635", "token": os.getenv('ENV_MARAJADOSENA_MA')},
    {"municipio": "Alagoinha", "id_sus": "260060", "token": os.getenv('ENV_ALAGOINHA_PE')},
    {"municipio": "Baraúna", "id_sus": "240145", "token": os.getenv('ENV_BARAUNA_RN')},
    {"municipio": "Jucuruçu", "id_sus": "291845", "token": os.getenv('ENV_JUCURUCU_BA')},
    {"municipio": "Vitorino Freire", "id_sus": "211300", "token": os.getenv('ENV_VITORINOFREIRE_MA')},
    {"municipio": "Brejo de Areia", "id_sus": "210215", "token": os.getenv('ENV_BREJODEAREIA_MA')},
    {"municipio": "Oiapoque", "id_sus": "160050", "token": os.getenv('ENV_OIAPOQUE_AP')},
    {"municipio": "Tarrafas", "id_sus": "231325", "token": os.getenv('ENV_TARRAFAS_CE')},
    {"municipio": "Salvaterra", "id_sus": "150630", "token": os.getenv('ENV_SALVATERRA_PA')},
    {"municipio": "Lagoa do Ouro", "id_sus": "260860", "token": os.getenv('ENV_LAGOADOOURO_PE')},
]
for municipio_id_sus in df_envio_turn['municipio_id_sus'].unique():
    send_data(df_envio_turn, municipio_id_sus)


