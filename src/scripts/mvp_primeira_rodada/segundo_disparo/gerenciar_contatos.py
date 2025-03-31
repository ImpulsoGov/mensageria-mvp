import os
import time
import pandas as pd
import requests

def enviar_mensagem(token_municipio, contato):
    """
    Envia uma mensagem para um cidadão usando a API do Turn.io.
    """
    whatsapp_id= contato["telefone"]

    headers = {
        'Authorization': f'Bearer {token_municipio}',
        'Accept': 'application/vnd.v1+json',
        'Content-Type': 'application/json'
    }

    data_message = {
        "preview_url": False,
        "recipient_type": "individual",
        "to": str(whatsapp_id),
        "type": "text",
        "text": {"body": "Este número pertence a ImpulsoGov."}
    }
    url_message = 'https://whatsapp.turn.io/v1/messages'

    try:
        response_message = requests.post(url_message, headers=headers, json=data_message)
        print(f"Resposta da mensagem para {whatsapp_id}: {response_message.text}")
        return response_message.ok
    except Exception as e:
        print(f"Erro ao enviar mensagem para 5511970632463: {e}")
    time.sleep(1.5)  # Pausa para respeitar limites da API

def atualizar_perfil(token_municipio, contato, linha_cuidado):
    """
    Atualiza o perfil de um cidadão usando a API do Turn.io.
    
    """
    whatsapp_id= contato["telefone"]

    headers = {
        'Authorization': f'Bearer {token_municipio}',
        'Accept': 'application/vnd.v1+json',
        'Content-Type': 'application/json'
    }

    json_data_profile = {
        "opted_in": True,
        "nome_do_paciente": contato["nome"],
        "linha_de_cuidado": linha_cuidado,
        "municipio": contato["municipio_id_sus"],
        "equipe_ine": contato["equipe_ine_vinc"],
        "equipe_nome": contato["equipe_nome"],
        "mvp_data_envio": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mvp_clique_botao_recente": '',
        "horarios_cronicos": contato["horarios_cito"],
        "horarios_cito": contato["horarios_cronicos"],
        "estabelecimento_documentos": contato["estabelecimento_documentos"],
        "estabelecimento_nome": contato["estabelecimento_nome"],
        "estabelecimento_telefone": contato["estabelecimento_telefone"],
        "estabelecimento_horario": contato["estabelecimento_horario"],
        "estabelecimento_endereco": contato["estabelecimento_endereco"]
    }
    url_profile = f'https://whatsapp.turn.io/v1/contacts/{whatsapp_id}/profile'

    try:
        response_profile = requests.patch(url_profile, headers=headers, json=json_data_profile)
        return response_profile.ok
    except Exception as e:
        print(f"Erro ao atualizar perfil de {whatsapp_id}: {e}")
    time.sleep(1)  # Pausa para respeitar limites da API


def adicionar_contato(token_municipio,contato,linha_cuidado):

    #mensagem_enviada = enviar_mensagem(token_municipio,contato)
    perfil_atualizado = atualizar_perfil(token_municipio,contato,linha_cuidado)
    return perfil_atualizado
# Fluxo principal
