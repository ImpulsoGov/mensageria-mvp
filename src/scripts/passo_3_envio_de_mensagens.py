# ### Programa mensagens
# A partir dos usuários que foram selecionados e enriquecidos os dados 
# programa o envio de mensagens


#### Configurações iniciais do ambiente
import os
import requests
import json
import time
import numpy as np
from dotenv import load_dotenv
import time
from datetime import datetime
import pandas as pd

from src.bd import BigQueryClient
from src.loggers import logger



tokens_municipios = [
    {"municipio": "Paulo Ramos", "id_sus": "210810", "token": os.getenv('ENV_PAULORAMOS_MA'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Lago Verde", "id_sus": "210590", "token": os.getenv('ENV_LAGOVERDE_MA'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Pacoti", "id_sus": "230980", "token": os.getenv('ENV_PACOTI_CE'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Monsenhor Tabosa", "id_sus": "230860", "token": os.getenv('ENV_MONSENHORTABOSA_CE'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Marajá do Sena", "id_sus": "210635", "token": os.getenv('ENV_MARAJADOSENA_MA'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Alagoinha", "id_sus": "260060", "token": os.getenv('ENV_ALAGOINHA_PE'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Baraúna", "id_sus": "240145", "token": os.getenv('ENV_BARAUNA_RN'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Jucuruçu", "id_sus": "291845", "token": os.getenv('ENV_JUCURUCU_BA'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Vitorino Freire", "id_sus": "211300", "token": os.getenv('ENV_VITORINOFREIRE_MA'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Brejo de Areia", "id_sus": "210215", "token": os.getenv('ENV_BREJODEAREIA_MA'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Oiapoque", "id_sus": "160050", "token": os.getenv('ENV_OIAPOQUE_AP'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Tarrafas", "id_sus": "231325", "token": os.getenv('ENV_TARRAFAS_CE'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Salvaterra", "id_sus": "150630", "token": os.getenv('ENV_SALVATERRA_PA'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
    {"municipio": "Lagoa do Ouro", "id_sus": "260860", "token": os.getenv('ENV_LAGOADOOURO_PE'), "link_imagem": "https://avatars.githubusercontent.com/u/63020100?s=280&v=4"},
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
    time.sleep(1)

    # 1. Configurar ambiente
    bq_client = BigQueryClient()  # Crie uma instância do cliente
    client = bq_client.client  # Use o cliente já configurado

    # update_query = f"""UPDATE `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens` SET mvp_status_envio = "{response.status_code}" WHERE celular_tratado = "{str(contato["celular_tratado"])}" and mvp_data_envio = "{str(contato["mvp_data_envio"])}";"""
    update_query = f"""UPDATE `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens_teste` SET mvp_status_envio = "{response.status_code}" WHERE celular_tratado = {str(contato["celular_tratado"])} and mvp_data_envio = "{str(contato["mvp_data_envio"])}" and municipio = "{contato["municipio"]}";"""
    update_job = client.query(update_query)
    if response.status_code == 201 or response.status_code == 200:
        print(f"Mensagem enviada para {whatsapp_id}")
    else:
        print(f"Falha ao enviar mensagem para {whatsapp_id}: {response.status_code}, {response.text}")
def seleciona_horario(contatos):
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
def programa_mensagens() -> None:
    #### Consulta dos dados
    # carregando a tabela de usuários selecionados
    # query = """
    #     SELECT *
    #     FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens`
    #     WHERE mvp_grupo = "teste" and mvp_data_envio = current_date("America/Sao_Paulo")
    # """

    #Configurar ambiente
    bq_client = BigQueryClient()  # Crie uma instância do cliente
    client = bq_client.client  # Use o cliente já configurado

    query = """
        SELECT *
        FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens_teste`
        WHERE mvp_grupo = "teste" and DATE(TIMESTAMP(mvp_data_envio), "America/Sao_Paulo") = DATE(current_datetime("America/Sao_Paulo"))"""
    query_job = client.query(query)
    contatos: pd.DataFrame = bq_client.consultar_dados(query)    
    contatos['whatsapp_id'] = contatos['celular_tratado']
    contatos = seleciona_horario(contatos)
    for index, row in contatos.iterrows():
        try:
            token_municipio = next((municipio["token"] for municipio in tokens_municipios if municipio["municipio"] == row["municipio"]), None)
            template = seleciona_template_por_linha_de_cuidado(row.to_dict())
            envia_mensagem(token_municipio, row.to_dict(), template)
        except Exception as e:
            print(f"Erro no envio do contato: {e}")
    return json.dumps({
        'status': 'sucesso',
        'mensagem': 'Mensagens enviados para o cidadão.'
    }), 200, {'Content-Type': 'application/json'}
