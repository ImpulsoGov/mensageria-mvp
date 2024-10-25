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

from src.bd import BigQueryClient
from src.loggers import logger


load_dotenv()

tokens_municipios = [
    {"municipio": "Paulo Ramos", "id_sus": "210810", "token": os.getenv('ENV_PAULORAMOS_MA')},
    {"municipio": "Pacoti", "id_sus": "210810", "token": os.getenv('ENV_PACOTI_CE')},
    {"municipio": "Marajá do Sena", "id_sus": "210810", "token": os.getenv('ENV_MARAJADOSENA_MA')},
    {"municipio": "Monsenhor Tabosa", "id_sus": "210810", "token": os.getenv('ENV_MONSENHORTABOSA_CE')},
    {"municipio": "Lago Verde", "id_sus": "210590", "token": os.getenv('ENV_LAGOVERDE_MA')},
    {"municipio": "Alagoinha", "id_sus": "260060", "token": os.getenv('ENV_ALAGOINHA_PE')},
    {"municipio": "Baraúna", "id_sus": "240145", "token": os.getenv('ENV_BARAUNA_RN')},
    {"municipio": "Jucuruçu", "id_sus": "291845", "token": os.getenv('ENV_JUCURUCU_BA')},
    {"municipio": "Vitorino Freire", "id_sus": "211300", "token": os.getenv('ENV_VITORINOFREIRE_MA')},
] 

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
    whatsapp_id = str(whatsapp_id)
    logger.info(f"Whatsapp_id:{whatsapp_id}")
    
    data = {
      "preview_url": False,
      "recipient_type": "individual",
      "to": whatsapp_id,
      "type": "text",
      "text": {"body": "Este número pertence a ImpulsoGov."}
    }
    url = 'https://whatsapp.turn.io/v1/messages'
    logger.info("Passou 8")
    response = requests.post(URL_API_MENSAGENS, headers=headers, json=data)
    time.sleep(1)
    logger.info("Passou 9")
    if response.status_code == 201 or response.status_code == 200:
        print(f"Mensagem enviada para {whatsapp_id}")
    else:
        print(f"Falha ao enviar mensagem para {whatsapp_id}: {response.status_code}, {response.text}")

    logger.info("Passou 10")


def programa_mensagens():

    # Configurar ambiente
    bq_client = BigQueryClient()  # Crie uma instância do cliente
    client = bq_client.client  # Use o cliente já configurado

    # Consulta ao BigQuery
    query = """
        SELECT *
        FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens_teste`
        WHERE mvp_grupo = "teste" AND DATE(TIMESTAMP(mvp_data_envio), "America/Sao_Paulo") = DATE(current_datetime("America/Sao_Paulo"))
    """
    
    df_historico_envio_mensagens = bq_client.consultar_dados(query)

    logger.info(f"Captura finalizada:{df_historico_envio_mensagens.shape[0]}")

    # Programa a mensagem
    for i in range(df_historico_envio_mensagens.shape[0]):  # Usando shape[0] para obter o número de linhas
        try:
            logger.info("Passou 1")
            token_municipio = next((municipio["token"] for municipio in tokens_municipios if municipio["municipio"] == df_historico_envio_mensagens.loc[i]["municipio"]), None)
            logger.info("Passou 2")
            hora_envio = df_historico_envio_mensagens.loc[i]["mvp_tipo_grupo"]
            logger.info("Passou 3")
            linha_cuidado = df_historico_envio_mensagens.loc[i]["linha_cuidado"]
            logger.info("Passou 4")
            template_linha_cuidado = "mensageria_usuarios_campanha_citopatologico_v01" if linha_cuidado == "cito" else "mensageria_usuarios_campanha_cronicos_v0"
            logger.info("Passou 5")
            celular_tratado = df_historico_envio_mensagens.loc[i]["celular_tratado"]
            logger.info("Passou 6")
            template = seleciona_template_por_linha_de_cuidado(template_linha_cuidado, df_historico_envio_mensagens.loc[i]["municipio"])
            logger.info("Passou 7")
            envia_mensagem(token_municipio, celular_tratado, template)  # Usando celular_tratado aqui
        except Exception as e:
            print(f"Erro na programação do contato: {e}")

# Exemplo de chamada da função
# programa_mensagens(client, tokens_municipios)


    return json.dumps({
        'status': 'sucesso',
        'mensagem': 'Mensagens enviados para o cidadão.'
    }), 200, {'Content-Type': 'application/json'}
