import os
import time
import pandas as pd
from typing import Tuple
import requests
from src.bd import BigQueryClient

# Dicionário com os tokens dos municípios
tokens_municipios = [
    {"municipio": "Paulo Ramos", "id_sus": "210810", "token": os.getenv('ENV_PAULORAMOS_MA')},
]

# Query para selecionar cidadãos
query = """
    WITH registros_por_municipio AS (
        SELECT
            municipio_id_sus,
            cidadao_nome,
            cidadao_cns,
            cidadao_cpf,
            cidadao_documento_identificador,
            cidadao_telefone,
            dt_nascimento,
            pertence_lista_citopatologico,
            pertence_lista_diabeticos,
            pertence_lista_hipertensos,
            linha_cuidado_selecionada,
            estabelecimento_cnes_vinculo,
            estabelecimento_nome,
            estabelecimento_endereco,
            estabelecimento_telefone,
            estabelecimento_documentos,
            estabelecimento_horario,
            equipe_ine_vinculo,
            equipe_nome,
            horarios_cito,
            horarios_cronicos,
            ROW_NUMBER() OVER (PARTITION BY municipio_id_sus ORDER BY cidadao_nome) AS row_num
        FROM `ip_mensageria_camada_prata.usuarios_mvp01_ciclo2`
        WHERE cidadao_telefone NOT IN (
            SELECT DISTINCT cidadao_telefone
            FROM `ip_mensageria_camada_prata.eventos_mvp01_ciclo2`
            WHERE status_evento = 1 -- Contato adicionado
        )
    )
    SELECT *
    FROM registros_por_municipio
    WHERE row_num <= 1;
"""

def selecionar_cidadaos() -> pd.DataFrame:
    """
    Consulta o BigQuery e retorna um DataFrame com os cidadãos selecionados.
    """
    bq_client = BigQueryClient()
    df: pd.DataFrame = bq_client.consultar_dados(query)
    return df

def enviar_mensagem(row, headers):
    """
    Envia uma mensagem para um cidadão usando a API do Turn.io.
    """
    data_message = {
        "preview_url": False,
        "recipient_type": "individual",
        "to": str("+5511970632463"),
        "type": "text",
        "text": {"body": "Este número pertence a ImpulsoGov."}
    }
    url_message = 'https://whatsapp.turn.io/v1/messages'

    try:
        response_message = requests.post(url_message, headers=headers, json=data_message)
        print(f"Resposta da mensagem para 5511970632463: {response_message.text}")
    except Exception as e:
        print(f"Erro ao enviar mensagem para 5511970632463: {e}")
    time.sleep(1.5)  # Pausa para respeitar limites da API

def atualizar_perfil(row, headers):
    """
    Atualiza o perfil de um cidadão usando a API do Turn.io.
    """
    json_data_profile = {
        "opted_in": True,
        "nome_do_paciente": 'Walter',
        "linha_de_cuidado": row.linha_cuidado_selecionada,
        "municipio": row.municipio_id_sus,
        "equipe_ine": row.equipe_ine_vinculo,
        "equipe_nome": row.equipe_nome,
        "mvp_data_envio": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "horarios_cronicos": row.horarios_cronicos,
        "horarios_cito": row.horarios_cito
    }
    url_profile = f'https://whatsapp.turn.io/v1/contacts/5511970632463/profile'

    try:
        response_profile = requests.patch(url_profile, headers=headers, json=json_data_profile)
        print(f"Resposta do perfil para 5511970632463: {response_profile.text}")
    except Exception as e:
        print(f"Erro ao atualizar perfil de 5511970632463: {e}")
    time.sleep(1)  # Pausa para respeitar limites da API

def registrar_evento(row, status_evento):
    bq_client = BigQueryClient()
    data_evento = {
        "municipio_id_sus": row.municipio_id_sus,
        "cidadao_nome": row.nome_do_paciente,
        "cidadao_cns": row.cidadao_cns,
        "cidadao_cpf": row.cidadao_cpf,
        "cidadao_documento_identificador": row.cidadao_documento_identificador,
        "cidadao_telefone": row.celular_tratado,
        "dt_nascimento": row.dt_nascimento,
        "linha_cuidado_selecionada": row.linha_cuidado,
        "estabelecimento_cnes_vinculo": row.estabelecimento_cnes,
        "equipe_ine_vinculo": row.equipe_ine,
        "status_evento": status_evento,
        "data_evento": pd.Timestamp.now()
    }
    try:
        bq_client.inserir_dados("ip_mensageria_camada_prata.eventos_mvp01_ciclo2", [data_evento])
        print(f"Evento registrado com sucesso para {row.celular_tratado}")
    except Exception as e:
        print(f"Erro ao registrar evento para {row.celular_tratado}: {e}")

def adicionar_contato(df, municipio_id_sus):
    token = next((municipio["token"] for municipio in tokens_municipios if municipio["id_sus"] == municipio_id_sus), None) 
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
        mensagem_enviada = enviar_mensagem(row, headers)
        if mensagem_enviada:
            perfil_atualizado = atualizar_perfil(row, headers)
            if perfil_atualizado:
                registrar_evento(row, status_evento=1)  # Contato adicionado
        time.sleep(1.5)

# Fluxo principal
if __name__ == "__main__":
    df = selecionar_cidadaos()
    for municipio in tokens_municipios:
        adicionar_contato(df, municipio["id_sus"])
