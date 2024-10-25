# ### Programa mensagens
# A partir dos usuários que foram selecionados e enriquecidos os dados 
# programa o envio de mensagens



#### Configurações iniciais do ambiente
import os
import requests
import json
from google.oauth2 import service_account
from datetime import datetime
from google.cloud import bigquery
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

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
credentials = service_account.Credentials.from_service_account_file('credencial_bigquery.json')
project_id = 'predictive-keep-314223'
client = bigquery.Client(credentials= credentials,project=project_id)
URL_API_MENSAGENS = "https://whatsapp.turn.io/v1/messages"
TEMPLATE_NAMESPACE = os.getenv('TEMPLATE_NAMESPACE')



#### Funcoes
def seleciona_template_por_linha_de_cuidado(linha_de_cuidado, municipio):
    if linha_de_cuidado == "mensageria_usuarios_campanha_citopatologico_v01":
        template = {
            "namespace": "TEMPLATE_NAMESPACE",  
            "name": linha_de_cuidado,
            "language": {
                "code": "pt",
                "policy": "deterministic"
            },
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "link": "https://url.com/video-file.mp4"
                            }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "="
                        },
                        {
                            "type": "text",
                            "text": "="
                        }
                    ]
                }
            ]
        }      
    elif linha_de_cuidado == "mensageria_usuarios_campanha_cronicos_v0":
        template = {
            "namespace": "TEMPLATE_NAMESPACE",  
            "name": linha_de_cuidado,
            "language": {
                "code": "pt",
                "policy": "deterministic"
            },
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "video",
                            "video": {
                                "link": "https://url.com/video-file.mp4"
                            }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "-" 
                        },
                        {
                            "type": "text",
                            "text": "-" 
                        }
                    ]
                }
            ]
        }      
    else:
        return None
    return template
def envia_mensagem(token, whatsapp_id, template):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.v1+json',
        'Content-Type': 'application/json'
    }
    # dados_de_envio = {
    #     "to" : whatsapp_id,
    #     "type" : "template",
    #     "template" : template
    # }
    # response = requests.post(URL_API_MENSAGENS, headers=headers, data=json.dumps(dados_de_envio))
    data = {
      "preview_url": False,
      "recipient_type": "individual",
      "to": whatsapp_id,
      "type": "text",
      "text": {"body": "Este número pertence a ImpulsoGov."}
    }
    url = 'https://whatsapp.turn.io/v1/messages'
    response = requests.post(URL_API_MENSAGENS, headers=headers, json=data)
    time.sleep(1)
    if response.status_code == 201 or response.status_code == 200:
        print(f"Mensagem enviada para {whatsapp_id}")
    else:
        print(f"Falha ao enviar mensagem para {whatsapp_id}: {response.status_code}, {response.text}")




#### Consulta dos dados
# carregando a tabela de usuários selecionados
# query = """
#     SELECT *
#     FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens`
#     WHERE mvp_grupo = "teste" and mvp_data_envio = current_date("America/Sao_Paulo")
# """
query = """
    SELECT *
    FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens_teste`
    WHERE mvp_grupo = "teste" and DATE(TIMESTAMP(mvp_data_envio), "America/Sao_Paulo") = DATE(current_datetime("America/Sao_Paulo"))"""
query_job = client.query(query)
rows = [dict(row) for row in query_job]
df_historico_envio_mensagens = pd.DataFrame(rows)



#### Programa a mensagem
for i in range(df_historico_envio_mensagens.size):
    try:
        token_municipio = next((municipio["token"] for municipio in tokens_municipios if municipio["municipio"] == df_historico_envio_mensagens.loc[i]["municipio"]), None)        
        hora_envio = df_historico_envio_mensagens.loc[i]["mvp_tipo_grupo"]
        linha_cuidado = df_historico_envio_mensagens.loc[i]["linha_cuidado"]
        template_linha_cuidado = "mensageria_usuarios_campanha_citopatologico_v01" if linha_cuidado == "cito" else "mensageria_usuarios_campanha_cronicos_v0"
        celular_tratado = df_historico_envio_mensagens.loc[i]["celular_tratado"]
        template = seleciona_template_por_linha_de_cuidado(template_linha_cuidado, df_historico_envio_mensagens.loc[i]["municipio"])
        envia_mensagem(token_municipio, token_municipio, template)
    except:
        print(f"Erro na programação do contato")