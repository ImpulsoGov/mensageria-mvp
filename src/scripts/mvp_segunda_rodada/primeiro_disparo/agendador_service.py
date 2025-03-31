import schedule
import time
from datetime import datetime
from abc import ABC, abstractmethod
from src.scripts.mvp_segunda_rodada.primeiro_disparo.campanha_service import CampanhaService
from src.scripts.mvp_segunda_rodada.primeiro_disparo.mensageria_service import EnvioMensagensService


class AgendadorService(ABC):
    @abstractmethod
    def executar(self):
        """Método obrigatório para execução do serviço"""
        pass

class CampanhaAgendada(AgendadorService):
    def __init__(self, municipio_id, campanha_nome, data_corrente):
        self.municipio_id = municipio_id
        self.campanha_nome = campanha_nome
        self.data_corrente = data_corrente if data_corrente is not None else str(datetime.today().strftime('%Y-%m-%d'))

    def executar(self):
        print(f"Executando CampanhaService às 7h para {self.municipio_id}")
        campanha_service = CampanhaService()
        campanha_service.executar_fluxo(
            municipio_id=self.municipio_id, 
            campanha_nome=self.campanha_nome, 
            data_corrente=self.data_corrente
        )

class MensageriaAgendada(AgendadorService):
    def __init__(self, envio_data, horarios, classificacao_experimento, mensagem_tipo):
        self.envio_data = envio_data
        self.horarios = horarios
        self.classificacao_experimento = classificacao_experimento
        self.mensagem_tipo = mensagem_tipo

    def executar(self):
        print(f"Executando EnvioMensagensService para {self.envio_data} nos horários {self.horarios}")
        disparador_service = EnvioMensagensService()
        for horario in self.horarios:
            disparador_service.realizar_envio(
                envio_data=self.envio_data, 
                horario_envio=horario, 
                classificacao_experimento=self.classificacao_experimento,
                mensagem_tipo=self.mensagem_tipo
            )

def agendar_tarefas(
    municipio_id, campanha_nome, data_corrente, 
    envio_data, horarios, classificacao_experimento, mensagem_tipo
):
    campanha = CampanhaAgendada(municipio_id, campanha_nome, data_corrente)
    mensageria = MensageriaAgendada(envio_data, horarios, classificacao_experimento, mensagem_tipo)

    schedule.every().day.at("16:07").do(campanha.executar)
    schedule.every().day.at("16:12").do(mensageria.executar)
    

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    print("Iniciando agendador...")
    agendar_tarefas(
        municipio_id="210535", 
        campanha_nome="mvp_ciclo2", 
        data_corrente="2025-03-31",
        envio_data="2025-03-31", 
        horarios=["8h", "12h", "16h"], 
        classificacao_experimento="teste", 
        mensagem_tipo="mensagem_inicial"
    )
