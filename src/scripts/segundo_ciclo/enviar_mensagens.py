from datetime import datetime
import json
import time
import psutil
import os
from typing import Final
import numpy as np
import pandas as pd
import pytz
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.bd import BigQueryClient
from src.loggers import logger
from src.scripts.segundo_ciclo.gerenciar_contatos import adicionar_contato
from src.scripts.segundo_ciclo.utilitarios import TOKENS_MUNICIPIOS, USUARIOS_COLUNAS_TIPOS, EVENTOS_COLUNAS_TIPOS, MENSAGEM_TEMPLATE

# Configurações globais e constantes
URL_API_MENSAGENS: Final[str] = "https://whatsapp.turn.io/v1/messages"
TEMPLATE_NAMESPACE: Final[str] = os.getenv("TEMPLATE_NAMESPACE")

QUERY_TEMPLATE: Final[str] = """
    SELECT *
    FROM `ip_mensageria_camada_prata.usuarios_mvp01_segundo_ciclo`
    WHERE 
      data_programada_segundo_ciclo = @data_programada_segundo_ciclo
      AND municipio_id_sus = @municipio_id_sus;
"""

# Funções utilitárias
def tratar_tipos_dados(registro: dict, tipos: dict) -> dict:
    """
    Trata os tipos de dados de um registro baseado nos tipos esperados.

    Args:
        registro (dict): Registro a ser tratado.
        tipos (dict): Mapeamento das colunas e seus tipos esperados.

    Returns:
        dict: Registro com os tipos tratados.
    """
    registro_tratado = {}
    for chave, tipo in tipos.items():
        valor = registro.get(chave)
        registro_tratado[chave] = None if valor in {None, pd.NA, "", "nan", "<NA>"} else tipo(valor)
    return registro_tratado

class ConsultaBigQueryException(Exception):
    """
    Exceção personalizada para erros durante consultas ao BigQuery.
    """
    pass

def selecionar_cidadaos(municipio_id_sus: str, data_programada: str) -> pd.DataFrame:
    """
    Consulta o BigQuery e retorna os cidadãos selecionados.

    Args:
        municipio_id_sus (str): ID do município SUS.
        data_programada (str): Data programada para o envio.

    Returns:
        pd.DataFrame: DataFrame com os cidadãos selecionados.

    Raises:
        ConsultaBigQueryException: Caso não existam registros ou ocorra algum erro.
    """
    query = QUERY_TEMPLATE.replace("@municipio_id_sus", f"'{municipio_id_sus}'").replace(
        "@data_programada_segundo_ciclo", f"DATE('{data_programada}')"
    )

    bq_client = BigQueryClient()

    try:
        df = bq_client.consultar_dados(query, USUARIOS_COLUNAS_TIPOS)

        if df.empty:
            logger.error('O DataFrame está vazio. Nenhum cidadão encontrado.')
            raise ConsultaBigQueryException('Nenhum cidadão encontrado na consulta.')

    except Exception as e:
        logger.error(f'Ocorreu um erro durante a execução da consulta: {e}')
        raise ConsultaBigQueryException(f'Erro ao consultar dados do BigQuery: {e}')

    return df

def definir_mensagem(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifica os registros em categorias de 1 a 9 de forma aleatória.

    Args:
        df (pd.DataFrame): DataFrame com os registros retornados pela função selecionar_cidadaos.

    Returns:
        pd.DataFrame: DataFrame com uma nova coluna 'mensagem_tipo', contendo valores aleatórios entre 1 e 9.

    Raises:
        ConsultaBigQueryException: Caso o DataFrame esteja vazio.
    """
    if df.empty:
        logger.error('O DataFrame está vazio. Nenhuma classificação será realizada.')
        raise ConsultaBigQueryException('O DataFrame está vazio. Nenhuma classificação será realizada.')

    df['mensagem_tipo'] = np.random.randint(1, 9, size=len(df))
    return df

def definir_template(contato: pd.Series) -> dict:
    """
    Define o template de mensagem baseado na linha de cuidado e tipo de mensagem.

    Args:
        contato (pd.Series): Dados do contato.
        linha_cuidado (str): Linha de cuidado associada ao contato.
        mensagem_tipo (int): Tipo da mensagem a ser enviada.

    Returns:
        dict: Template formatado para envio da mensagem.
    """
    municipio_id_sus = contato["municipio_id_sus"]
    linha_cuidado = contato["linha_cuidado"]
    mensagem_tipo = contato["mensagem_tipo"]

    if linha_cuidado in MENSAGEM_TEMPLATE and mensagem_tipo in MENSAGEM_TEMPLATE[linha_cuidado]:
        template_tipo, versao, tipo, link_func = MENSAGEM_TEMPLATE[linha_cuidado][mensagem_tipo]

        link = link_func(
            municipio_id_sus=municipio_id_sus, 
            template_tipo=template_tipo,
            linha_cuidado=linha_cuidado
        ) if callable(link_func) else link_func

        header_component = None
        body_component = {
            "type": "body",
            "parameters": [
                {"type": "text", "text": contato["nome"]},
                {"type": "text", "text": contato["municipio_nome"]},
            ],
        }

        if mensagem_tipo not in (3, 6, 9):
            header_component = {
                "type": "header",
                "parameters": [{"type": tipo, tipo: {"link": link}}]
            }

        components = [comp for comp in [header_component, body_component] if comp is not None]

        return {
            "namespace": TEMPLATE_NAMESPACE,
            "name": f'mensageria_usuarios_{linha_cuidado}_{template_tipo}_{versao}',
            "language": {"code": "pt_BR", "policy": "deterministic"},
            "components": components,
        }
    return {}

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10), 
    stop=stop_after_attempt(3),
)
def envia_mensagem(token_municipio: str, whatsapp_id: str, template: dict) -> requests.Response:
    """
    Envia uma mensagem via API WhatsApp Turn.io.

    Args:
        token_municipio (str): Token do município para autenticação.
        whatsapp_id (str): ID do WhatsApp do destinatário.
        template (dict): Template da mensagem.

    Returns:
        requests.Response: Resposta da API.

    Raises:
        requests.HTTPError: Caso a requisição falhe.
    """
    headers = {
        'Authorization': f'Bearer {token_municipio}',
        'Accept': 'application/vnd.v1+json',
        'Content-Type': 'application/json'
    }
    dados_de_envio = {
        "to": str(whatsapp_id),
        "type": "template",
        "template": template
    }
    response = requests.post(URL_API_MENSAGENS, headers=headers, data=json.dumps(dados_de_envio))
    response.raise_for_status()
    time.sleep(1.05)
    return response

def inserir_registro_evento(
        contato: dict,
        data_programada: str, 
        evento_status: int, 
        evento_status_code: int = None,
        evento_message_code: str = None
    ) -> dict:
    """
    Insere registros na tabela de eventos no BigQuery.

    Args:
        contato (dict): Dados do contato.
        data_programada (str): Data programada do evento.
        evento_status (int): Status do evento.
        evento_status_code (int, optional): Código do status do evento.
        evento_message_code (str, optional): Código da mensagem associada ao evento.

    Returns:
        dict: Resultado da operação.

    Raises:
        Exception: Caso ocorra erro ao inserir dados no BigQuery.
    """
    try:
        registro = {
            **contato,
            "evento_status": evento_status,
            "evento_status_code": evento_status_code,
            "evento_message_code": evento_message_code,
            "evento_data": data_programada,
            "criacao_data": datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S"),
            "atualizacao_data": datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S"),
        }
        registro_tratado = tratar_tipos_dados(registro, EVENTOS_COLUNAS_TIPOS)
        tabela = "predictive-keep-314223.ip_mensageria_camada_prata.eventos_mvp01_segundo_ciclo"
        BigQueryClient().inserir_dados(tabela, [registro_tratado])
        return {"status": "sucesso", "mensagem": "Registro inserido com sucesso."}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

def processar_envios(
        municipio_id_sus: str, 
        data_programada: str
    ) -> dict:
    """
    Processa o envio de mensagens para cidadãos.

    Args:
        municipio_id_sus (str): ID do município SUS.
        data_programada (str): Data programada para o envio.
        linha_cuidado (str): Linha de cuidado associada.
        mensagem_tipo (str): Tipo da mensagem a ser enviada.

    Returns:
        dict: Estatísticas do processamento, incluindo contatos notificados e uso de memória/tempo.
    """
    inicio = time.time()
    processo = psutil.Process(os.getpid())
    memoria_inicial = processo.memory_info().rss
    contatos_notificados = 0

    logger.info(f'Consultando usuários do município {municipio_id_sus}')
    df_cidadaos = selecionar_cidadaos(municipio_id_sus, data_programada)

    logger.info(f'Classificando os cidadãos para envio de mensagens')
    df_classificado = definir_mensagem(df_cidadaos)
    df_classificado.loc[df_classificado["municipio_nome"] == "Lagoa do Ouro", "municipio_nome"] = "Lagoa do ouro"

    contatos = df_classificado.to_dict(orient="records")

    for contato in contatos:
        token_municipio = next(
            (mun["token"] for mun in TOKENS_MUNICIPIOS if mun["municipio"] == contato["municipio_nome"]), None
        )
        template = definir_template(contato=contato)

        if template and token_municipio:
            try:
                logger.info(f'Registrando evento de seleção para {contato["nome"]}')
                inserir_registro_evento(contato=contato, data_programada=data_programada, evento_status=1)

                logger.info(f'Enviando mensagem para {contato["telefone"]}')
                resposta = envia_mensagem(token_municipio, contato["telefone"], template)

                logger.info(f'Registrando envio bem-sucedido para {contato["telefone"]}')
                inserir_registro_evento(
                    contato=contato,
                    data_programada=data_programada,
                    evento_status=3,
                    evento_status_code=resposta.status_code,
                    evento_message_code=resposta.text
                )

                if resposta.status_code == 200:
                    contatos_notificados += 1
            except Exception as e:
                logger.error(f'Erro ao enviar mensagem para {contato["telefone"]}: {e}')
                inserir_registro_evento(
                    contato=contato,
                    data_programada=data_programada,
                    evento_status=3,
                    evento_status_code=500,
                    evento_message_code=str(e)
                )

    fim = time.time()
    memoria_final = processo.memory_info().rss
    memoria_processada = memoria_final - memoria_inicial  
    tempo_execucao = fim - inicio  

    return {
        'status': 200,
        'mensagem': f'Mensagens enviadas para os cidadãos.',
        'contatos_notificados': contatos_notificados,
        'tempo_execucao_segundos': round(tempo_execucao, 2),  # Tempo de execução em segundos
        'memoria_processada_mb': round(memoria_processada / (1024 ** 2), 2)  # Memória processada em MB
    }



