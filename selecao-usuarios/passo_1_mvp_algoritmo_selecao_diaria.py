### Seleção diária dos cidadãos para envio de mensagens
# Escolhe usuarios para participação da pesquisa, os subdividindo em diferentes categorias, 
# que resulta em uma tabela que fica armazenada no BigQuery como 
# "ip_mensageria_camada_prata.historico_envio_mensagens".



#### Configurações iniciais do ambiente
import pandas as pd
import io
import numpy as np
from sklearn.model_selection import train_test_split
from google.oauth2 import service_account
from datetime import datetime
import locale
from google.cloud import bigquery
credentials = service_account.Credentials.from_service_account_file('credencial_bigquery.json')
project_id = 'predictive-keep-314223'
client = bigquery.Client(credentials= credentials,project=project_id)



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
def dividir_grupos_equilibrado(df, num_grupos=3):
    # Função para dividir os usuários em grupos de horários das mensagens
    def dividir_municipio(grupo):
        grupo_size = len(grupo)
        grupos = np.tile(range(1, num_grupos + 1), grupo_size // num_grupos + 1)[:grupo_size]
        np.random.shuffle(grupos)
        return grupos
    #considerando a divisão em equipes
    df['horario_grupo'] = df.groupby('equipe_ine')['equipe_ine'].transform(dividir_municipio)
    return df



#### Consulta dos dados
# Histórico e divisão dos grupos de teste e controle
query = """
    SELECT *
    FROM `predictive-keep-314223.ip_mensageria_camada_prata.divisao_teste_controle_equipes`
"""
query_job = client.query(query)
rows = [dict(row) for row in query_job]
df = pd.DataFrame(rows)
# # Dados atualizados para confirmação de pendência
query = """
    SELECT *
    FROM `predictive-keep-314223.ip_mensageria_camada_prata.unificado_lista_com_telefones_grupos_atendimentos_`
"""
query_job = client.query(query)
rows = [dict(row) for row in query_job]
df_pendencias = pd.DataFrame(rows)
# Histórico de envios anteriores
query = """
    SELECT *
    FROM `predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens`
"""
query_job = client.query(query)
rows = [dict(row) for row in query_job]
df_historico_envio_mensagens = pd.DataFrame(rows)




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
# df['nome_do_paciente'] = df['nome_do_paciente'].astype(str)
# df_pendencias['nome_do_paciente'] = df_pendencias['nome_do_paciente'].astype(str)
# df['data_de_nascimento'] = pd.to_datetime(df['data_de_nascimento'], errors='coerce')
# df_pendencias['data_de_nascimento'] = pd.to_datetime(df_pendencias['data_de_nascimento'], errors='coerce')
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
else:
    df_filtrado = df_unificado


### Tratamento dos celulares
# Filtrando casos com o celular preenchido incorreto
df_filtrado = df_filtrado[df_filtrado['celular_tratado']!=0]
# Adicionando 55 no início do telefone
df_filtrado['celular_tratado'] = df_filtrado['celular_tratado'].astype(str)
df_filtrado['caracteres_celular'] = df_filtrado['celular_tratado'].str.len()
df_filtrado['celular_tratado'] = df_filtrado.apply(trata_celular,axis=1)
# Data de último exame
df_filtrado['data_exame_cito'] = df_filtrado['data_exame_cito'].astype('datetime64[ns]')
df_filtrado['data_afericao_hipertensos'] = df_filtrado['data_afericao_hipertensos'].astype('datetime64[ns]')
df_filtrado['data_exame_diabeticos'] = df_filtrado['data_exame_diabeticos'].astype('datetime64[ns]')
df_filtrado['data_ultimo_exame'] = df_filtrado.apply(ultimo_exame,axis=1)



#### Divisão por horários
df_dividido = dividir_grupos_equilibrado(df_filtrado)
# Máximo de 15 pessoas por equipe, dia e linha de cuidado -> máximo de 5 pessoas por horário, equipe, dia e linha de cuidado
df_envio_diario = df_dividido.groupby(['municipio','equipe_ine','linha_cuidado','horario_grupo','grupo']).apply(lambda x: x.sample(min(len(x), 5))).reset_index(drop=True)
# Ajuste no formato da coluna de tipo de grupo
dia_semana = datetime.now().strftime('%a').upper()
df_envio_diario['mvp_tipo_grupo'] = dia_semana+'_H'+df_envio_diario['horario_grupo'].astype(str).str.zfill(2)
df_envio_diario= df_envio_diario.rename(columns={'grupo':'mvp_grupo'})
df_envio_dia_atual = df_envio_diario[['municipio','municipio_id_sus', 'equipe_ine', 'equipe_nome', 'linha_cuidado','nome_do_paciente','data_de_nascimento','celular_tratado','mvp_tipo_grupo','mvp_grupo','numero_visitas_ubs_ultimos_12_meses','data_ultimo_exame']]
df_envio_dia_atual['mvp_data_envio'] = datetime.today().strftime('%Y-%m-%d')
df_envio_dia_atual['mvp_data_envio'] = df_envio_dia_atual['mvp_data_envio'].astype('datetime64[ns]')
df_envio_dia_atual['celular_tratado'] = df_envio_dia_atual['celular_tratado'].astype(str)
df_envio_dia_atual['mvp_tipo_grupo'] = df_envio_dia_atual['mvp_tipo_grupo'].astype(str)
df_envio_dia_atual['mvp_data_envio'] = df_envio_dia_atual['mvp_data_envio'].astype('datetime64[ns]')
df_envio_dia_atual['mvp_grupo'] = df_envio_dia_atual['mvp_grupo'].astype('str')
df_envio_dia_atual['numero_visitas_ubs_ultimos_12_meses'] = df_envio_dia_atual['numero_visitas_ubs_ultimos_12_meses'].astype(int)
df_envio_dia_atual['data_ultimo_exame'] = pd.to_datetime(df_envio_dia_atual['data_ultimo_exame'], errors='coerce')
df_envio_dia_atual['data_de_nascimento'] = pd.to_datetime(df_envio_dia_atual['data_de_nascimento'], errors='coerce')
# Adicionar dados na tabela de histórico
table_id = "predictive-keep-314223.ip_mensageria_camada_prata.historico_envio_mensagens"
# Incremento com os dados do dia atual
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
job = client.load_table_from_dataframe(df_envio_dia_atual, table_id, job_config=job_config)
