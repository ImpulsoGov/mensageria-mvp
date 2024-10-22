import os
import requests
import json
from dotenv import load_dotenv
# ### Envio de mensagens

# A partir dos usuários que foram selecionados e enriquecidos os dados envia programa seu envio de mensagem.

# #### Configurações iniciais do ambiente
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

# #### Programa a mensagem

contatos = [
    {"whatsapp_id": "5583999568450", "nome_do_paciente": "João", "municipio_id_sus": "210810", "municipio": "Paulo Ramos", "linha_de_cuidado": "cito"},
    {"whatsapp_id": "5583999667449", "nome_do_paciente": "Maria", "municipio_id_sus": "210810", "municipio": "Paulo Ramos", "linha_de_cuidado": "cronicos"},
]

def seleciona_token_por_municipio(id_sus):
    for municipio in tokens_municipios:
        if municipio["id_sus"] == id_sus:
            return municipio["token"]
    return None  
def seleciona_template_por_linha_de_cuidado(contato):
    nome_template_cito = "mensageria_usuarios_campanha_citopatologico_v01"
    nome_template_cronicos = "mensageria_usuarios_campanha_cronicos_v0"
    if contato['linha_de_cuidado'] == "cito":
        template_nome = nome_template_cito
    elif contato['linha_de_cuidado'] == "cronicos":
        template_nome = nome_template_cronicos
    else:
        return None
    template = {
            "namespace": "TEMPLATE_NAMESPACE",  
            "name": template_nome,
            "language": {
                "code": "pt",
                "policy": "deterministic"
            },
            "components": [
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
   

def envia_mensagem(token, whatsapp_id, template):
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

    if response.status_code == 201 or response.status_code == 200:
        print(f"Mensagem enviada para {whatsapp_id}")
    else:
        print(f"Falha ao enviar mensagem para {whatsapp_id}: {response.status_code}, {response.text}")

for contato in contatos:
    token_valor = seleciona_token_por_municipio(contato["municipio_id_sus"])
    whatsapp_id = contato["whatsapp_id"]
    template = seleciona_template_por_linha_de_cuidado(contato)

    if token_valor:
        envia_mensagem(token_valor, whatsapp_id, template)
    else:
        print(f"Não foi encontrado token para o municipio {contato['municipio_id_sus']}")       