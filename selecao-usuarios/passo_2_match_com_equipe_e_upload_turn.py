### Match com equipe e Upload na Turn
# A partir dos usuários selecionados para o dia no Passo 1, une suas informações com suas informações 
# de equipe/estabelecimentos que esta no Big Query e advem da Turn. Após isso da upload desses contatos na turn.


#### Configurações iniciais do ambiente
import pandas as pd
import io
import numpy as np
from sklearn.model_selection import train_test_split
from google.oauth2 import service_account
from datetime import datetime
from google.cloud import bigquery
import requests
import json
import time
from dotenv import load_dotenv
import os
credentials = service_account.Credentials.from_service_account_file('credencial_bigquery.json')
project_id = 'predictive-keep-314223'
client = bigquery.Client(credentials= credentials,project=project_id)


#### Match
# Une dados da tabela de seção diaria "ip_mensageria_camada_prata.historico_envio_mensagens" do BigQuery 
# com os dados do estabelecimento que a pessoa é pertencente, por meio do dos dados que estão registradas 
# na view "ip_mensageria_camada_prata.contact_details_turnio" no BigQuery.



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
tokens_municipios = [
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


