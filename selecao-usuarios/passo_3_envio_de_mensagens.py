# ### Programa mensagens
# A partir dos usuários que foram selecionados e enriquecidos os dados 
# programa o envio de mensagens



#### Configurações iniciais do ambiente
import os
import requests
import json
import time
from datetime import datetime
import pandas as pd

from google.oauth2 import service_account
from google.cloud import bigquery
from dotenv import load_dotenv
load_dotenv()

credentials = service_account.Credentials.from_service_account_file('credencial_bigquery.json')
project_id = 'predictive-keep-314223'
client = bigquery.Client(credentials= credentials,project=project_id)

tokens_municipios = [
    {"municipio": "Paulo Ramos", "id_sus": "210810", "token": os.getenv('ENV_PAULORAMOS_MA'), "link_imagem": "https://i.imgur.com/zn7sRTV.png"},
    {"municipio": "Monsenhor Tabosa", "id_sus": "230860", "token": os.getenv('ENV_MONSENHORTABOSA_CE'), "link_imagem": "https://i.imgur.com/5r2R0vz.png"},
    {"municipio": "Pacoti", "id_sus": "230980", "token": os.getenv('ENV_PACOTI_CE'), "link_imagem": "https://i.imgur.com/TWkhHBq.png"},
    {"municipio": "Lago Verde", "id_sus": "210590", "token": os.getenv('ENV_LAGOVERDE_MA'), "link_imagem": "https://i.imgur.com/AzH0p2d.png"},
    {"municipio": "Marajá do Sena", "id_sus": "210635", "token": os.getenv('ENV_MARAJADOSENA_MA'), "link_imagem": "https://i.imgur.com/PHEjjwW.png"},
    {"municipio": "Alagoinha", "id_sus": "260060", "token": os.getenv('ENV_ALAGOINHA_PE'), "link_imagem": "https://i.imgur.com/Hn7Z9TI.png"},
    {"municipio": "Baraúna", "id_sus": "240145", "token": os.getenv('ENV_BARAUNA_RN'), "link_imagem": "https://i.imgur.com/aQDjqJv.png"},
    {"municipio": "Jucuruçu", "id_sus": "291845", "token": os.getenv('ENV_JUCURUCU_BA'), "link_imagem": "https://i.imgur.com/Rp2zq72.png"},
    {"municipio": "Tarrafas", "id_sus": "231325", "token": os.getenv('ENV_TARRAFAS_CE'), "link_imagem": "https://i.imgur.com/G4scY7R.png"},
    {"municipio": "Salvaterra", "id_sus": "150630", "token": os.getenv('ENV_SALVATERRA_PA'), "link_imagem": "https://i.imgur.com/bnwogCJ.png"},
    {"municipio": "Lagoa do Ouro", "id_sus": "260860", "token": os.getenv('ENV_LAGOADOOURO_PE'), "link_imagem": "https://i.imgur.com/xGLsHnO.png"},
    # {"municipio": "Vitorino Freire", "id_sus": "211300", "token": os.getenv('ENV_VITORINOFREIRE_MA'), "link_imagem": "https://i.imgur.com/BmqRuY0.png"},
    # {"municipio": "Brejo de Areia", "id_sus": "210215", "token": os.getenv('ENV_BREJODEAREIA_MA'), "link_imagem": "https://i.imgur.com/tO0qHav.png"},
    # {"municipio": "Oiapoque", "id_sus": "160050", "token": os.getenv('ENV_OIAPOQUE_AP'), "link_imagem": "https://i.imgur.com/ZlHJHcR.png"},
]

URL_API_MENSAGENS = "https://whatsapp.turn.io/v1/messages"
TEMPLATE_NAMESPACE = os.getenv('TEMPLATE_NAMESPACE')



#### Funcoes
def seleciona_template_por_linha_de_cuidado(contato):
    nome_template_cito = "mensageria_usuarios_campanha_citopatologico_v01"
    nome_template_cronicos = "mensageria_usuarios_campanha_cronicos_v0"
    if contato['linha_cuidado'] == "citopatologico":
        template_nome = nome_template_cito
        type_header = "image"
        link_media = next((municipio["link_imagem"] for municipio in tokens_municipios if municipio["municipio"] == contato["municipio"]), None)
    elif contato['linha_cuidado'] == "cronicos":
        template_nome = nome_template_cronicos
        type_header="video"
        link_media= "https://i.imgur.com/gHWgdG4.mp4"
    else:
        return None
    template = {
            "namespace": TEMPLATE_NAMESPACE,
            "name": template_nome,
            "language": {
                "code": "pt_BR",
                "policy": "deterministic"
            },
            "components": [
                {
                    "type" : "header",
                    "parameters": [
                        {
                            "type": type_header,
                            type_header: {
                            "link": link_media
                        }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": contato['nome_do_paciente']
                        },
                        {
                            "type": "text",
                            "text": contato['municipio']
                        }
                    ]
                }
            ]
        }
    return template
def envia_mensagem(token, contato, template):
    whatsapp_id = str(contato["whatsapp_id"])
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.v1+json',
        'Content-Type': 'application/json'
    }
    dados_de_envio = {
        "to" : whatsapp_id,
        "type" : "template",
        "template" : template
    }
    response = requests.post(URL_API_MENSAGENS, headers=headers, data=json.dumps(dados_de_envio))
    time.sleep(1.05)

    update_query = f"""UPDATE `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens` SET mvp_status_envio = "{response.status_code}" WHERE celular_tratado = "{str(contato["celular_tratado"])}" and mvp_data_envio = "{str(contato["mvp_data_envio"])}";"""
    update_job = client.query(update_query)
    if response.status_code == 201 or response.status_code == 200:
        print(f"Mensagem enviada para {whatsapp_id}")
    else:
        print(f"Falha ao enviar mensagem para {whatsapp_id}: {response.status_code}, {response.text}")
def seleciona_horario(contato):
    status_respostas_unicas = contatos.groupby("mvp_tipo_grupo")["mvp_status_envio"].apply(lambda x: list(x.unique())).reset_index()
    if not status_respostas_unicas[(status_respostas_unicas["mvp_tipo_grupo"].str.contains("H01")) & (status_respostas_unicas["mvp_status_envio"].apply(lambda x: x == [None]))].empty:
        return contatos[contatos['mvp_tipo_grupo'].str.contains("H01")]
    elif not status_respostas_unicas[(status_respostas_unicas["mvp_tipo_grupo"].str.contains("H02")) & (status_respostas_unicas["mvp_status_envio"].apply(lambda x: x == [None]))].empty:
        resultado = contatos[(contatos['mvp_tipo_grupo'].str.contains("H02")) | 
                            ((contatos['mvp_tipo_grupo'].str.contains("H01")) & (contatos['mvp_status_envio'].isna()))]
        return resultado
    else:
        resultado = contatos[(contatos['mvp_tipo_grupo'].str.contains("H03")) | 
                            ((contatos['mvp_tipo_grupo'].str.contains("H02")) & (contatos['mvp_status_envio'].isna())) | 
                            ((contatos['mvp_tipo_grupo'].str.contains("H01")) & (contatos['mvp_status_envio'].isna()))]
        return resultado




#### Consulta dos dados
# carregando a tabela de usuários selecionados
query = """
    SELECT *
    FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens`
    WHERE mvp_grupo = "teste" and mvp_data_envio = current_date("America/Sao_Paulo")
"""
query_job = client.query(query)
rows = [dict(row) for row in query_job]
contatos = pd.DataFrame(rows)
contatos['whatsapp_id'] = contatos['celular_tratado']


# Comentando pois não vamos mais fazer seleção pelo horário
# contatos = seleciona_horario(contatos)

#### USEI ISSO AQUI PARA IR MUNICIPIO A MUNICIPIO ####
# contatos = contatos[contatos['municipio'] == 'Lagoa do ouro'] 
# contatos = contatos.reset_index(drop=True)

contatos.loc[contatos['municipio'] == 'Lagoa do ouro', 'municipio'] = 'Lagoa do Ouro'
#### Programa a mensagem
for i in range(len(contatos.index)):
    try:
        token_municipio = next((municipio["token"] for municipio in tokens_municipios if municipio["municipio"] == contatos.loc[i]["municipio"]), None)
        template = seleciona_template_por_linha_de_cuidado(contatos.loc[i])
        envia_mensagem(token_municipio, contatos.loc[i], template)
    except:
        print(f"Erro no envio do contato")
