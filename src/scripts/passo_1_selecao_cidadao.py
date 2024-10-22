import pandas as pd
from google.cloud import bigquery
import numpy as np
from typing import Any,Tuple
import json

from src.bd import BigQueryClient

# Função para identificar pendências nas linhas de cuidado
def identificar_pendencias(df_pendencias: pd.DataFrame) -> pd.DataFrame:
    df_pendencias['citopatologico_pendente_atual'] = df_pendencias['status_exame'].apply(
        lambda x: True if x in ('exame_nunca_realizado', 'exame_vencido', 'exame_vence_no_quadrimestre_atual') else False
    )
    df_pendencias['cronicos_pendente_atual'] = df_pendencias.apply(pendencia_cronicos, axis=1)
    return df_pendencias

# Função para verificar pendência de crônicos
def pendencia_cronicos(x: pd.Series) -> bool:
    if (x['esta_na_lista_hipertensos'] and (not x['realizou_afericao_ultimos_6_meses'] or not x['realizou_consulta_hip_ultimos_6_meses'])) or \
       (x['esta_na_lista_diabeticos'] and (not x['realizou_consulta_dia_ultimos_6_meses'] or not x['realizou_solicitacao_hemoglobina_ultimos_6_meses'])):
        return True
    return False

# Função para unificar dados históricos e pendências
def unificar_dados(df: pd.DataFrame, df_pendencias: pd.DataFrame) -> pd.DataFrame:
    df['municipio_id_sus'] = df['municipio_id_sus'].fillna(0).astype(int).astype(str)
    df_pendencias['municipio_id_sus'] = df_pendencias['municipio_id_sus'].fillna(0).astype(int).astype(str)
    df_pendencias['equipe_ine'] = df['equipe_ine'].fillna(0).astype(int).astype(str)
    
    df_unificado = df.merge(df_pendencias, how='right', on=['nome_do_paciente', 'data_de_nascimento', 'municipio_id_sus'])
    df_unificado['pendencia_atualizada'] = df_unificado.apply(pendencia_atualizada, axis=1)
    return df_unificado[df_unificado['pendencia_atualizada']].drop_duplicates()

# Função para verificar se há pendência atualizada
def pendencia_atualizada(x: pd.Series) -> bool:
    if x['linha_cuidado'] == 'cronicos' and x['cronicos_pendente_atual']:
        return True
    elif x['linha_cuidado'] == 'citopatologico' and x['citopatologico_pendente_atual']:
        return True
    return False

# Função para filtrar histórico de envio de mensagens
def filtrar_historico(df_unificado: pd.DataFrame, df_historico_envio_mensagens: pd.DataFrame) -> pd.DataFrame:
    df_unificado['chave_cidadao'] = df_unificado['nome_do_paciente'].astype(str) + '_' + df_unificado['data_de_nascimento'].astype(str)
    
    if not df_historico_envio_mensagens.empty:
        df_historico_envio_mensagens['chave_cidadao'] = df_historico_envio_mensagens['nome_do_paciente'].astype(str) + '_' + df_historico_envio_mensagens['data_de_nascimento'].astype(str)
        return df_unificado[~df_unificado['chave_cidadao'].isin(df_historico_envio_mensagens['chave_cidadao'])]
    
    return df_unificado

# Função para tratar os números de celular
def tratar_telefones(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['celular_tratado'] != 0]
    df['celular_tratado'] = df['celular_tratado'].astype(str)
    df['caracteres_celular'] = df['celular_tratado'].str.len()
    df['celular_tratado'] = df.apply(trata_celular, axis=1)
    return df

# Função para adicionar o código do país no celular
def trata_celular(x: pd.Series) -> Any:
    if x['caracteres_celular'] == 10:
        return "55" + x['celular_tratado'][:2] + "9" + x['celular_tratado'][2:]
    elif x['caracteres_celular'] == 11:
        return "55" + x['celular_tratado']
    return None

# Função para processar a data do último exame
def processar_exames(df: pd.DataFrame) -> pd.DataFrame:
    df['data_exame_cito'] = df['data_exame_cito'].astype('datetime64[ns]')
    df['data_afericao_hipertensos'] = df['data_afericao_hipertensos'].astype('datetime64[ns]')
    df['data_exame_diabeticos'] = df['data_exame_diabeticos'].astype('datetime64[ns]')
    df['data_ultimo_exame'] = df.apply(ultimo_exame, axis=1)
    return df

# Função para determinar a data do último exame
def ultimo_exame(x: pd.Series) -> pd.Timestamp:
    if x['linha_cuidado'] == 'citopatologico':
        return x['data_exame_cito']
    elif x['linha_cuidado'] == 'cronicos' and x['hipertensao_pendente'] and x['diabetes_pendente']:
        return max(x['data_afericao_hipertensos'], x['data_exame_diabeticos'])
    elif x['linha_cuidado'] == 'cronicos' and x['hipertensao_pendente']:
        return x['data_afericao_hipertensos']
    return x['data_exame_diabeticos']

# Função para dividir cidadãos em grupos equilibrados
def dividir_grupos_equilibrado(df: pd.DataFrame, num_grupos: int = 3) -> pd.DataFrame:
    def dividir_municipio(grupo: pd.Series) -> np.ndarray:
        grupo_size = len(grupo)
        grupos = np.tile(range(1, num_grupos + 1), grupo_size // num_grupos + 1)[:grupo_size]
        np.random.shuffle(grupos)
        return grupos
    df['horario_grupo'] = df.groupby('equipe_ine')['equipe_ine'].transform(dividir_municipio)
    return df

# Função para selecionar cidadãos para envio de mensagens
def selecionar_cidadaos_para_envio(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(['municipio', 'equipe_ine', 'linha_cuidado', 'horario_grupo', 'grupo']).apply(
        lambda x: x.sample(min(len(x), 5))
    ).reset_index(drop=True)

# Função para preparar os dados para envio
def preparar_para_envio(df: pd.DataFrame) -> pd.DataFrame:
    dia_semana = pd.to_datetime('today').strftime('%a').upper()
    df['mvp_tipo_grupo'] = dia_semana + '_H' + df['horario_grupo'].astype(str).str.zfill(2)
    df['mvp_data_envio'] = pd.to_datetime(pd.Timestamp.today().strftime('%Y-%m-%d'))
    return df[['municipio', 'municipio_id_sus', 'equipe_ine', 'equipe_nome', 'linha_cuidado',
               'nome_do_paciente', 'data_de_nascimento', 'celular_tratado', 'mvp_tipo_grupo', 'mvp_grupo',
               'numero_visitas_ubs_ultimos_12_meses', 'data_ultimo_exame', 'mvp_data_envio']]

# Função para atualizar o histórico de envios no BigQuery
def atualizar_historico(client: bigquery.Client, df: pd.DataFrame, table_id: str) -> None:
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
    client.load_table_from_dataframe(df, table_id, job_config=job_config)

def processa_passo_1(project_id: str) -> Tuple[str, int, dict]:
    """
    Função que processa diariamente o envio de mensagens para cidadãos de acordo com critérios definidos.
    
    Args:
        request (Request): Objeto de requisição HTTP contendo os dados do projeto e credenciais.
    
    Returns:
        Tuple[str, int, dict]: Resposta HTTP contendo o status, mensagem e os dados processados.
    """
    # 1. Configurar ambiente
    bq_client = BigQueryClient()
    client = bq_client.configurar_ambiente()
    
    # 2. Consultar dados
    query_df = f"SELECT * FROM `{project_id}.ip_mensageria_camada_prata.divisao_teste_controle_equipes`"
    df: pd.DataFrame = bq_client.bq_client.consultar_dados(client, query_df)
    
    query_df_pendencias = f"SELECT * FROM `{project_id}.ip_mensageria_camada_prata.unificado_lista_com_telefones_grupos_atendimentos_`"
    df_pendencias: pd.DataFrame = bq_client.consultar_dados(client, query_df_pendencias)
    
    query_df_historico_envio_mensagens = f"SELECT * FROM `{project_id}.ip_mensageria_camada_prata.historico_envio_mensagens`"
    df_historico_envio_mensagens: pd.DataFrame = bq_client.consultar_dados(client, query_df_historico_envio_mensagens)
    
    # 3. Preparar dados
    df_pendencias = identificar_pendencias(df_pendencias)
    df_unificado: pd.DataFrame = unificar_dados(df, df_pendencias)
    df_filtrado: pd.DataFrame = filtrar_historico(df_unificado, df_historico_envio_mensagens)
    df_filtrado: pd.DataFrame = tratar_telefones(df_filtrado)
    df_filtrado: pd.DataFrame = processar_exames(df_filtrado)
    
    # 4. Dividir e selecionar cidadãos para envio
    df_dividido: pd.DataFrame = dividir_grupos_equilibrado(df_filtrado)
    df_envio_diario: pd.DataFrame = selecionar_cidadaos_para_envio(df_dividido)
    
    # 5. Preparar dados para envio e atualizar histórico
    df_envio_dia_atual: pd.DataFrame = preparar_para_envio(df_envio_diario)
    atualizar_historico(client, df_envio_dia_atual, f"{project_id}.ip_mensageria_camada_prata.historico_envio_mensagens")

    # Retornar sucesso com os dados preparados
    return json.dumps({
        'status': 'sucesso',
        'mensagem': 'Dados processados e histórico atualizado.',
        'dados_enviados': df_envio_dia_atual.to_dict(orient='records')
    }), 200, {'Content-Type': 'application/json'}