import json
import pandas as pd
import requests
import os
import time
from typing import List, Dict, Tuple

from src.bd import BigQueryClient


# Lista de tokens de municípios
TOKEN_MUNICIPIOS = [
        {"municipio": "Paulo Ramos", "id_sus": "210810", "token": os.getenv('ENV_PAULORAMOS_MA')},
        {"municipio": "Pacoti", "id_sus": "230980", "token": os.getenv('ENV_PACOTI_CE')},
        {"municipio": "Marajá do Sena", "id_sus": "210635", "token": os.getenv('ENV_MARAJADOSENA_MA')},
        {"municipio": "Monsenhor Tabosa", "id_sus": "230860", "token": os.getenv('ENV_MONSENHORTABOSA_CE')},
        {"municipio": "Lago Verde", "id_sus": "210590", "token": os.getenv('ENV_LAGOVERDE_MA')},
        {"municipio": "Alagoinha", "id_sus": "260060", "token": os.getenv('ENV_ALAGOINHA_PE')},
        {"municipio": "Baraúna", "id_sus": "240145", "token": os.getenv('ENV_BARAUNA_RN')},
        {"municipio": "Jucuruçu", "id_sus": "291845", "token": os.getenv('ENV_JUCURUCU_BA')},
        {"municipio": "Vitorino Freire", "id_sus": "211300", "token": os.getenv('ENV_VITORINOFREIRE_MA')},
    ]

# Função para obter o token do município
def capturar_token(municipio_id_sus: str, tokens_municipios: List[Dict[str, str]]) -> str:
    """
    Retorna o token associado a um município com base no seu ID SUS.

    Args:
        municipio_id_sus (str): O ID SUS do município.
        tokens_municipios (List[Dict[str, str]]): Lista de dicionários contendo informações dos municípios e seus tokens.

    Returns:
        str: O token do município ou None se não for encontrado.
    """
    for token_info in tokens_municipios:
        if token_info['id_sus'] == municipio_id_sus:
            return token_info['token']
    return None

# Função para enviar os dados para o Turn.io
def enviar_dados(df: pd.DataFrame, municipio_id_sus: str, tokens_municipios: List[Dict[str, str]]) -> None:
    """
    Envia os dados dos cidadãos para o Turn.io, utilizando o token correspondente ao município.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados filtrados por município.
        municipio_id_sus (str): O ID SUS do município.
        tokens_municipios (List[Dict[str, str]]): Lista de tokens para os diferentes municípios.
    """
    token = capturar_token(municipio_id_sus, tokens_municipios)
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

        # Atualiza o opted_in
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

# Função para fazer o merge dos dados e preparar o DataFrame para envio
def preparar_dados_envio(
    df_historico: pd.DataFrame, df_ibge: pd.DataFrame, df_contatos_turnio: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Prepara os dados para envio ao unir os dados de histórico de envio de mensagens com as informações do IBGE e Turn.io.

    Args:
        df_historico (pd.DataFrame): DataFrame contendo o histórico de envio de mensagens.
        df_ibge (pd.DataFrame): DataFrame com informações dos municípios obtidos do IBGE.
        df_contatos_turnio (pd.DataFrame): DataFrame com os contatos extraídos do Turn.io.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Um DataFrame com municípios únicos e outro DataFrame com os dados prontos para envio.
    """
    df_ibge['id_sus'] = df_ibge['id_sus'].astype(str)
    df_historico['municipio_id_sus'] = df_historico['municipio_id_sus'].astype(str)

    # Merge da tabela de usuários com a de municípios
    df_historico = pd.merge(df_historico, df_ibge[['id_sus', 'nome', 'uf_sigla']], left_on=['municipio_id_sus'], right_on=['id_sus'], how='left')

    df_contatos_turnio[['municipio', 'uf']] = df_contatos_turnio['details_municipio'].str.split(' - ', expand=True)

    # Equipes com preenchimento dos dados
    df_contatos_turnio_preenchido = df_contatos_turnio[df_contatos_turnio['details_equipe_nome'].notnull()]
    df_contatos_turnio_preenchido = df_contatos_turnio_preenchido[['details_equipe_nome', 'municipio', 'uf']].drop_duplicates().reset_index(drop=True)

    # Merge das tabelas de usuários e estabelecimento
    df = pd.merge(df_historico, df_contatos_turnio, left_on=['equipe_nome', 'municipio', 'uf_sigla'], right_on=['details_equipe_nome', 'municipio', 'uf'], how='left')

    df_envio_turn = df[['municipio', 'uf_sigla', 'municipio_id_sus', 'equipe_ine', 'equipe_nome', 'linha_cuidado',
                        'nome_do_paciente', 'data_de_nascimento', 'celular_tratado', 'mvp_tipo_grupo', 'mvp_data_envio',
                        'mvp_grupo', 'details_horarios_cronicos', 'details_telefone', 'details_estabelecimento_endereco',
                        'details_estabelecimento_telefone', 'details_estabelecimento_nome', 'details_horarios_cito',
                        'details_estabelecimento_documentos', 'details_estabelecimento_horario']]

    df_envio_turn = df_envio_turn.rename(columns={
        'details_horarios_cronicos': 'horarios_cronicos',
        'details_telefone': 'telefone',
        'details_estabelecimento_endereco': 'estabelecimento_endereco',
        'details_estabelecimento_telefone': 'estabelecimento_telefone',
        'details_estabelecimento_nome': 'estabelecimento_nome',
        'details_horarios_cito': 'horarios_cito',
        'details_estabelecimento_documentos': 'estabelecimento_documentos',
        'details_estabelecimento_horario': 'estabelecimento_horario'
    })

    df_envio_turn.drop_duplicates(subset=['municipio_id_sus', 'municipio'], inplace=True)

    return df_envio_turn

# Função principal
def processo_envio_turn() -> None:
    """
    Executa o processo de envio de mensagens para cidadãos de municípios brasileiros através da integração com Turn.io.
    Faz o merge dos dados, consulta os tokens, e envia as mensagens.
    """
    bq_client = BigQueryClient()
    client = bq_client.configurar_ambiente()

    # Consulta dos dados
    df_historico = client.consultar_dados(client, "SELECT * FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens`")
    df_ibge = client.consultar_dados(client, "SELECT * FROM `predictive-keep-314223.lista_de_codigos.municipios_ibge`")
    df_contatos_turnio = client.consultar_dados(client, "SELECT * FROM `predictive-keep-314223.ip_mensageria_camada_prata.contact_details_turnio`")

    # Preparar dados para envio
    df_envio_turn = preparar_dados_envio(df_historico, df_ibge, df_contatos_turnio)


    # Enviar dados para Turn.io
    for municipio_id_sus in df_envio_turn['municipio_id_sus'].unique():
        enviar_dados(df_envio_turn, municipio_id_sus, tokens_municipios=TOKEN_MUNICIPIOS)
    
    # Retornar sucesso com os dados preparados
    return json.dumps({
        'status': 'sucesso',
        'mensagem': 'Dados enviados para TurnIO.'
    }), 200, {'Content-Type': 'application/json'}
