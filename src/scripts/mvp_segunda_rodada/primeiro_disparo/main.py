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

# Classifica aleatoriamente as unidades de saúde em grupo controle ou tratamento



# Para cada unidade no grupo de tratamento checa o total de pessoas vinculadas e os dias restantes da campanha. 
# A razão entre os dois números será o total de pessoas a serem notificadas no dia

# Para cada unidade escolhe aleatoriamente as pessoas vinculadas conforme o total de pessoas a serem notificadas no dia 

# Para cada pessoa a ser notificada no dia, cria um campo 'mensagem_template_id' com valor aleatorio de 1 a 9. 
# Cria o campo horario_grupo scolhe aleatoriamente entre os valores '8h', '12h' e '16h'

# Insere as pessoas classificadas em uma tabela do big query chamada 'cidadaos_selecionados' informando mensagem_template_id, horario_grupo

from src.scripts.mvp_segunda_rodada.primeiro_disparo.campanha_service import CampanhaService
from src.scripts.mvp_segunda_rodada.primeiro_disparo.mensageria_service import EnvioMensagensService
import schedule
import time

def executar_campanha_e_envio():
    projeto_gcp = "predictive-keep-314223"
    
    # Passo 1: Executar o fluxo de campanha (definir classificação e registrar cidadãos selecionados)
    campanha_service = CampanhaService(projeto_gcp)
    # Para cada municipio:
    campanha_service.executar_fluxo(municipio_id="261220", campanha_nome="mvp_ciclo2")
    
    # Passo 2: Criar uma instância de EnvioMensagensService
    envio_service = EnvioMensagensService(projeto_gcp)
    
    # Passo 3: Agendar os envios (8h, 12h e 16h)
    envio_service.agendar_envios()

# Agendar a execução de campanha e envio para as 7h todos os dias
schedule.every().day.at("07:00").do(executar_campanha_e_envio)

print("Programa ativo, aguardando a execução agendada...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Checa a cada minuto se há uma tarefa agendada
