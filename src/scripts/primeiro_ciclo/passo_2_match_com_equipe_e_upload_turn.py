### Match com equipe e Upload na Turn
# A partir dos usuários selecionados para o dia no Passo 1, une suas informações com suas informações 
# de equipe/estabelecimentos que esta no Big Query e advem da Turn. Após isso da upload desses contatos na turn.


#### Configurações iniciais do ambiente
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

from src.bd import BigQueryClient
from src.loggers import logger


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


#### Funcoes
@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10), 
    stop=stop_after_attempt(3),
)
def send_one(celular_tratado, token) -> requests.Response:
    url_message = 'https://whatsapp.turn.io/v1/messages'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.v1+json',
        'Content-Type': 'application/json'
    }
    data_message = {
        "preview_url": False,
        "recipient_type": "individual",
        "to": str(celular_tratado),
        "type": "text",
        "text": {"body": "Este número pertence a ImpulsoGov."}
    }
    logger.info(f'Enviando mensagem para {celular_tratado}')
    response = requests.post(url_message, headers=headers, json=data_message)
    response.raise_for_status()
    logger.info(
        f'Mensagem enviada para {celular_tratado} '
        f'({response.status_code})'
    )
    return response


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10), 
    stop=stop_after_attempt(3),
)
def update_user_profile(
    celular_tratado,
    data_profile,
    token,
) -> requests.Response:
    url_profile = 'https://whatsapp.turn.io/v1/contacts/{}/profile'.format(
        celular_tratado,
    )
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.v1+json',
        'Content-Type': 'application/json'
    }
    logger.info(f'Atualizando perfil para {celular_tratado}')
    response = requests.patch(url_profile, headers=headers, json=data_profile)
    response.raise_for_status()
    logger.info(
        f'Perfil atualizado para {celular_tratado} '
        f'({response.status_code})'
    )
    return response


def send_data(df, municipio_id_sus):
    logger.info(f'Enviando mensagens para {municipio_id_sus}')
    logger.info('Obtendo tokens')
    token = next((municipio["token"] for municipio in tokens_municipios if municipio["id_sus"] == municipio_id_sus), None) 
    if not token:
        logger.error(f"Token não encontrado para {municipio_id_sus}")
        return

    df_filtered = df[df['municipio_id_sus'] == municipio_id_sus]
    logger.info(f'Enviamndo mensagens para {len(df_filtered)} usuários')

    for _, row in df_filtered.iterrows():
        try:
            response_message = send_one(row.celular_tratado, token=token)
            logger.debug(
                f'Resposta da mensagem para {row.celular_tratado}: '
                f'{response_message.text}'
            )
            time.sleep(1)
        except Exception as e:
            logger.error(
                f'Erro ao enviar mensagem para {row.celular_tratado}: {e}'
            )
            continue

        #atualiza opted_in
        json_data_profile = {
            "opted_in": True,
            "nome_do_paciente": row.nome_do_paciente,
            "linha_de_cuidado": row.linha_cuidado ,
            "municipio": row.municipio,
            "municipio_id_sus": row.municipio_id_sus,
            "equipe_ine": row.equipe_ine,
            "equipe_nome": row.equipe_nome,
            "mvp_tipo_grupo": row.mvp_tipo_grupo,
            "mvp_data_envio": row.mvp_data_envio.strftime("%Y-%m-%d %H:%M:%S"),
            "mvp_grupo": row.mvp_grupo,
            "estabelecimento_horario": row.estabelecimento_horario,
            "estabelecimento_documentos": row.estabelecimento_documentos,
            "estabelecimento_nome": row.estabelecimento_nome,
            "estabelecimento_endereco": row.estabelecimento_endereco,
            "estabelecimento_telefone": row.estabelecimento_telefone,
            "horarios_cronicos": row.horarios_cronicos,
            "horarios_cito": row.horarios_cito
        }
        try:
            response_profile = update_user_profile(
                row.celular_tratado,
                json_data_profile,
                token=token,
            )
            logger.debug(
                f'Resposta do perfil para {row.celular_tratado}: '
                f'{response_profile.text}'
            )
            time.sleep(1)
        except Exception as e:
            logger.error(
                f'Erro ao atualizar perfil de {row.celular_tratado}: {e}'
            )

        time.sleep(1)


def processo_envio_turn() -> None:
    logger.info('Iniciando processo de envio para TurnIO')

    logger.info('Configurando ambiente')
    bq_client = BigQueryClient()
    bq_client.configurar_ambiente()

    #### Consulta dos dados
    logger.info('Consultando dados')
    query = """
        SELECT *
        FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens`
        WHERE mvp_data_envio = current_date("America/Sao_Paulo") AND mvp_grupo='teste'
    """
    df_historico_envio_mensagens: pd.DataFrame = bq_client.consultar_dados(
        query,
    )
    # carregando dados dos municipios da tabela do ibge
    logger.info('Consultando dados - IBGE')
    query = """
        SELECT *
        FROM `predictive-keep-314223.lista_de_codigos.municipios_ibge`
    """
    df_ibge: pd.DataFrame = bq_client.consultar_dados(query)
    # carregando a view com dados da Turn io
    logger.info('Consultando dados - TurnIO')
    query = """
        SELECT *
        FROM `predictive-keep-314223.ip_mensageria_camada_prata.contact_details_turnio`
    """
    df_contatos_turnio: pd.DataFrame = bq_client.consultar_dados(query)


    #### Match
    # Une dados da tabela de seção diaria "ip_mensageria_camada_prata.historico_envio_mensagens" do BigQuery 
    # com os dados do estabelecimento que a pessoa é pertencente, por meio do dos dados que estão registradas 
    # na view "ip_mensageria_camada_prata.contact_details_turnio" no BigQuery.
    logger.info('Matching com equipes')
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
    df_envio_turn = df[['municipio','uf_sigla','municipio_id_sus','equipe_ine','equipe_nome',
                                                'linha_cuidado','nome_do_paciente','data_de_nascimento',
                                                'celular_tratado','mvp_tipo_grupo','mvp_data_envio',
                                                'mvp_grupo','details_horarios_cronicos','details_telefone',
                                                'details_estabelecimento_endereco',
                                                'details_estabelecimento_telefone',
                                                'details_estabelecimento_nome','details_horarios_cito',
                                                'details_estabelecimento_documentos',
                                                'details_estabelecimento_horario']]
    df_envio_turn = df_envio_turn.rename(columns={'details_horarios_cronicos':'horarios_cronicos',
                                                'details_telefone':'telefone',
                                                'details_estabelecimento_endereco':'estabelecimento_endereco',
                                                'details_estabelecimento_telefone':'estabelecimento_telefone',
                                                'details_estabelecimento_nome':'estabelecimento_nome',
                                                'details_horarios_cito':'horarios_cito',
                                                'details_estabelecimento_documentos':'estabelecimento_documentos',
                                                'details_estabelecimento_horario':'estabelecimento_horario'})
    df_envio_turn[['municipio_id_sus','municipio']].drop_duplicates()
    logger.info(f'Registros para envio para TurnIO: {len(df_envio_turn)}')

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
    logger.info('Enviando mensagens para TurnIO')
    for municipio_id_sus in df_envio_turn['municipio_id_sus'].unique():
        send_data(df_envio_turn, municipio_id_sus)
    # Retornar sucesso com os dados preparados
    logger.success('Dados enviados para TurnIO')

    return {
        'status': 'sucesso',
        'mensagem': 'Dados enviados para TurnIO'
    }
