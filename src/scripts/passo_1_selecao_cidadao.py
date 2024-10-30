### Seleção diária dos cidadãos para envio de mensagens
# Escolhe usuarios para participação da pesquisa, os subdividindo em diferentes categorias, 
# que resulta em uma tabela que fica armazenada no BigQuery como 
# "ip_mensageria_camada_prata.historico_envio_mensagens".


#### Configurações iniciais do ambiente
from datetime import datetime
import locale
from google.cloud import bigquery
import json
import numpy as np
import pandas as pd
from typing import Any,Tuple
from src.bd import BigQueryClient
import random
import io
import tempfile

#### Funcoes
def pendencia_atualizada(x):
    if x['linha_cuidado']=='cronicos' and x['cronicos_pendente_atual']==True:
        return True
    elif x['linha_cuidado']=='citopatologico' and x['citopatologico_pendente_atual']==True:
        return True
    else:
        return False
def trata_celular(x):
    if x['caracteres_celular']==10:
        return "55" + x['celular_tratado'][:2]+"9"+x['celular_tratado'][2:]
    elif x['caracteres_celular']==11:
        return "55" + x['celular_tratado']
    else:
        return None
def ultimo_exame(x):
    if x['linha_cuidado']=='citopatologico':
        return x['data_exame_cito']
    elif x['linha_cuidado']=='cronicos' and (x['hipertensao_pendente']== True and x['diabetes_pendente']==True):
        return max(x['data_afericao_hipertensos'], x['data_exame_diabeticos'])
    elif x['linha_cuidado']=='cronicos' and x['hipertensao_pendente']== True:
        return x['data_afericao_hipertensos']
    else:
        return x['data_exame_diabeticos']
def pendencia_cronicos(x):
    if (x['esta_na_lista_hipertensos'] == True and (x['realizou_afericao_ultimos_6_meses'] == False or x['realizou_consulta_hip_ultimos_6_meses'] == False)) or (x['esta_na_lista_diabeticos'] == True and (x['realizou_consulta_dia_ultimos_6_meses'] == False or x['realizou_solicitacao_hemoglobina_ultimos_6_meses'] == False)):
        return True
    else:
        return False
def selecionar_usuarios(df, max_usuarios=15):
    return df.groupby(['municipio', 'equipe_ine', 'linha_cuidado','grupo']).apply(
        lambda x: x.sample(min(len(x), max_usuarios))
    ).reset_index(drop=True)
# função para dividir os grupos de horários
def dividir_grupos_equilibrado(grupo, num_grupos=3):
    grupo_size = len(grupo)
    base_size = grupo_size // num_grupos
    extra = grupo_size % num_grupos
    
    grupos = [i + 1 for i in range(num_grupos) for _ in range(base_size)]
    grupos += [i + 1 for i in range(extra)]
    random.shuffle(grupos)
    
    return pd.Series(grupos, index=grupo.index)
def distribuir_em_horarios(df, num_grupos=3):
    df['horario_grupo'] = df.groupby(['municipio', 'equipe_ine', 'linha_cuidado','grupo'], group_keys=False).apply(
        lambda x: dividir_grupos_equilibrado(x, num_grupos).astype(int)
    )
    return df
def selecionar_cidadaos() -> Tuple[str, int, dict]:
    """
    Função que processa diariamente o envio de mensagens para cidadãos de acordo com critérios definidos.
    
    Args:
        project_id (str): O ID do projeto no BigQuery.
    
    Returns:
        Tuple[str, int, dict]: Resposta HTTP contendo o status, mensagem e os dados processados.
    """
    # 1. Configurar ambiente
    bq_client = BigQueryClient()  # Crie uma instância do cliente
    client = bq_client.client  # Use o cliente já configurado

    #### Consulta dos dados
    # Histórico e divisão dos grupos de teste e controle
    query = """
        SELECT *
        FROM `predictive-keep-314223.ip_mensageria_camada_prata.divisao_teste_controle_equipes`
    """
    df: pd.DataFrame = bq_client.consultar_dados(query)

    # # Dados atualizados para confirmação de pendência
    query = """
        SELECT *
        FROM `predictive-keep-314223.ip_mensageria_camada_prata.unificado_lista_com_telefones_grupos_atendimentos`
    """
    df_pendencias: pd.DataFrame = bq_client.consultar_dados(query)
    # Histórico de envios anteriores
    query = """
        SELECT *
        FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens`
    """
    df_historico_envio_mensagens: pd.DataFrame = bq_client.consultar_dados(query)

    #### Preparação dos dados
    # Identificação dos cidadãos com pendências em cito
    df_pendencias['citopatologico_pendente_atual'] = df_pendencias['status_exame'].apply(lambda x: True if x in ('exame_nunca_realizado','exame_vencido','exame_vence_no_quadrimestre_atual') else False)
    # Função para identificar crônicos em pendência
    df_pendencias['cronicos_pendente_atual'] = df_pendencias.apply(pendencia_cronicos,axis=1)
    # Junção dos dados históricos com a verificação de pendência atual
    # Converter as colunas 'municipio_id_sus' para o mesmo tipo (string)
    df['municipio_id_sus'] = df['municipio_id_sus'].fillna(0).astype(int).astype(str)
    df_pendencias['municipio_id_sus'] = df_pendencias['municipio_id_sus'].fillna(0).astype(int).astype(str)
    df_pendencias['equipe_ine'] = df['equipe_ine'].fillna(0).astype(int).astype(str)
    df_pendencias['cns'] = df['cns'].fillna(0).astype(int).astype(str)
    df['celular_tratado'] = df['celular_tratado'].fillna(0).astype(int).astype(str)
    df_pendencias = df_pendencias[['nome_do_paciente','data_de_nascimento','municipio_id_sus','citopatologico_pendente_atual','cronicos_pendente_atual']]
    df_unificado = df.merge(df_pendencias, how='right', on=['nome_do_paciente','data_de_nascimento','municipio_id_sus'])
    # Verificaçao se a linha de cuidado ainda está pendente
    df_unificado['pendencia_atualizada'] = df_unificado.apply(pendencia_atualizada,axis=1)
    df_unificado = df_unificado[df_unificado['pendencia_atualizada']==True]
    df_unificado = df_unificado.drop_duplicates()
    df_unificado['chave_cidadao'] = df_unificado['nome_do_paciente'].astype(str) + '_' + df_unificado['data_de_nascimento'].astype(str)
    if not(df_historico_envio_mensagens.empty):
        df_historico_envio_mensagens['chave_cidadao'] = df_historico_envio_mensagens['nome_do_paciente'].astype(str) + '_' + df_historico_envio_mensagens['data_de_nascimento'].astype(str)
        # Filtrando cidadãos que já receberam a mensagem
        df_filtrado = df_unificado[~df_unificado['chave_cidadao'].isin(df_historico_envio_mensagens['chave_cidadao'])]
        df_filtrado = df_filtrado[~df_filtrado['celular_tratado'].isin(df_historico_envio_mensagens['celular_tratado'])]
    else:
        df_filtrado = df_unificado


    ### Tratamento dos celulares
    # Filtrando casos com o celular preenchido incorreto
    df_filtrado = df_filtrado[df_filtrado['celular_tratado']!=0]
    df_filtrado = df_filtrado[df_filtrado['celular_tratado'].notnull()]
    df_filtrado = df_filtrado[df_filtrado['celular_tratado']!='0']
    # Adicionando 55 no início do telefone
    df_filtrado['celular_tratado'] = df_filtrado['celular_tratado'].astype(str)
    df_filtrado['caracteres_celular'] = df_filtrado['celular_tratado'].str.len()
    df_filtrado['celular_tratado'] = df_filtrado.apply(trata_celular,axis=1)
    df_filtrado = df_filtrado[~(df_filtrado['celular_tratado'].str.contains('00000000') | df_filtrado['celular_tratado'].str.contains('99999999'))]
    # Garantindo a não duplicação de celulares
    df_filtrado = df_filtrado.drop_duplicates().reset_index(drop=True)
    df_filtrado = df_filtrado.drop_duplicates(subset=['celular_tratado']).reset_index(drop=True)
    # Data de último exame
    df_filtrado['data_exame_cito'] = df_filtrado['data_exame_cito'].astype('datetime64[ns]')
    df_filtrado['data_afericao_hipertensos'] = df_filtrado['data_afericao_hipertensos'].astype('datetime64[ns]')
    df_filtrado['data_exame_diabeticos'] = df_filtrado['data_exame_diabeticos'].astype('datetime64[ns]')


    #### Divisão por horários
    df_selecionados = selecionar_usuarios(df_filtrado, max_usuarios=15)
    df_envio_diario = distribuir_em_horarios(df_selecionados)
    # Ajuste no formato da coluna de tipo de grupo
    dia_semana = datetime.now().strftime('%a').upper()
    df_envio_diario['mvp_tipo_grupo'] = dia_semana+'_H'+df_envio_diario['horario_grupo'].astype(str).str.zfill(2)
    df_envio_diario= df_envio_diario.rename(columns={'grupo':'mvp_grupo'})
    df_envio_diario['data_ultimo_exame_cito'] = df_envio_diario['data_exame_cito'].astype('datetime64[ns]')
    df_envio_diario['data_ultima_afericao_hipertensos'] = df_envio_diario['data_afericao_hipertensos'].astype('datetime64[ns]')
    df_envio_diario['data_ultimo_exame_diabeticos'] = df_envio_diario['data_exame_diabeticos'].astype('datetime64[ns]')
    df_envio_dia_atual = df_envio_diario[['municipio','municipio_id_sus', 'equipe_ine', 'equipe_nome', 'linha_cuidado','nome_do_paciente','data_de_nascimento','celular_tratado','mvp_tipo_grupo','mvp_grupo','numero_visitas_ubs_ultimos_12_meses','data_ultimo_exame_cito','data_ultima_afericao_hipertensos','data_ultimo_exame_diabeticos']]
    df_envio_dia_atual['mvp_data_envio'] = datetime.today().strftime('%Y-%m-%d')
    df_envio_dia_atual['mvp_data_envio'] = df_envio_dia_atual['mvp_data_envio'].astype('datetime64[ns]')
    df_envio_dia_atual['celular_tratado'] = df_envio_dia_atual['celular_tratado'].astype(str)
    df_envio_dia_atual['mvp_tipo_grupo'] = df_envio_dia_atual['mvp_tipo_grupo'].astype(str)
    df_envio_dia_atual['mvp_data_envio'] = df_envio_dia_atual['mvp_data_envio'].astype('datetime64[ns]')
    df_envio_dia_atual['mvp_grupo'] = df_envio_dia_atual['mvp_grupo'].astype('str')
    df_envio_dia_atual['numero_visitas_ubs_ultimos_12_meses'] = df_envio_dia_atual['numero_visitas_ubs_ultimos_12_meses'].astype(int)
    df_envio_dia_atual['data_de_nascimento'] = pd.to_datetime(df_envio_dia_atual['data_de_nascimento'], errors='coerce')
    # Adicionar dados na tabela de histórico
    table_id = "predictive-keep-314223.ip_mensageria_camada_prata.teste_historico"
    """
    # Incremento com os dados do dia atual
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
    job = client.load_table_from_dataframe(df_envio_dia_atual, table_id, job_config=job_config)
    """
    print(df_envio_dia_atual.head())
    print(df_envio_dia_atual.info())
    # Salvando o DataFrame em um arquivo CSV temporário
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as tmp:
        df_envio_dia_atual.to_csv(tmp.name, index=False, encoding="utf-8")
        tmp.seek(0)  # Retorna ao início do arquivo após escrever

        # Configurando a tabela e o job_config
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            write_disposition="WRITE_APPEND",
            field_delimiter=','
        )

        # Carregando o arquivo CSV para a tabela no BigQuery
        with open(tmp.name, "rb") as file_obj:
            job = client.load_table_from_file(file_obj, table_id, job_config=job_config)
            job.result()
            
    # Retornar sucesso com os dados preparados
    return {
        'status': 'sucesso',
        'mensagem': 'Mensagens enviadas para os cidadãos.'
    }

