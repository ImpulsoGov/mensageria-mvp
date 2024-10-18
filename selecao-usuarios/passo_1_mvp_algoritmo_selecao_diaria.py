### Seleção diária dos cidadãos para envio de mensagens
# Escolhe usuarios para participação da pesquisa, os subdividindo em diferentes categorias, 
# que resulta em uma tabela que fica armazenada no BigQuery como 
# "ip_mensageria_camada_prata.historico_envio_mensagens".

#### Configurações iniciais do ambiente
from google.cloud import bigquery
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file('credencial_bigquery.json')
project_id = 'predictive-keep-314223'
client = bigquery.Client(credentials= credentials,project=project_id)

#### Consulta e preparação dos dados

#### Divisão por horários