import schedule
import time
from datetime import datetime
from src.bd import BigQueryClient


class EnvioMensagensService:
    def __init__(self):
        self.client = BigQueryClient()

    def checar_cidadaos_para_envio(
            self,
            envio_data:str, 
            horario_envio: str, 
            classificacao_experimento:str, 
            mensagem_tipo:str
            ):
        query = f"""
            SELECT * 
            FROM `predictive-keep-314223.ip_mensageria_camada_ouro.cidadao_selecionado`
            WHERE envio_data_programado = '{envio_data}' AND envio_horario_programado = '{horario_envio}'
            AND classificacao_experimento = '{classificacao_experimento}' AND mensagem_tipo_programado = '{mensagem_tipo};
        """
        # Consultar os cidadãos que precisam ser enviados hoje
        cidadaos_df = self.client.consultar_dados(query)
        return cidadaos_df

    def realizar_envio(self, envio_data: str, horario_envio: str, classificacao_experimento: str, mensagem_tipo:str):
        cidadaos_para_envio = self.checar_cidadaos_para_envio(envio_data, horario_envio, classificacao_experimento, mensagem_tipo)

        print(f"Total de cidadãos para envio: {len(cidadaos_para_envio)}")

        if not cidadaos_para_envio.empty:
            for index, cidadao in cidadaos_para_envio.iterrows():
                print(f"Enviando mensagem para {cidadao['cidadao_telefone']}")  # Teste antes do envio
                self.enviar_mensagem(cidadao)
                self.registrar_evento(cidadao)
        else:
            print(f"Não há cidadãos para enviar mensagem no horário das {horario_envio}.")

    
    def registrar_evento(self, contato):
        try:
            registro = {
                "cidadao_id": contato['cidadao_id'],
                "cidadao_telefone": contato['cidadao_telefone'],
                "campanha_nome": contato['campanha_nome'],
                "mensagem_tipo": contato['mensagem_tipo_programado'],
                "mensagem_template": contato['mensagem_template'],
                "mensagem_midia_link": contato['mensagem_midia_link'],
                "mensagem_status": 'sucesso',
                "mensagem_status_code": '',
                "envio_data": contato['envio_data_programado'],
                "envio_horario": contato['envio_horario_programado'],
            }

            tabela = "predictive-keep-314223.ip_mensageria_camada_ouro.cidadao_mensageria"
            self.client.inserir_dados(tabela, [registro])

            print("Registro inserido com sucesso.")
            return {"status": "sucesso", "mensagem": "Registro inserido com sucesso."}
        except Exception as e:
            print(f"Erro ao registrar evento: {e}")
            return {"status": "erro", "mensagem": str(e)}


    def enviar_mensagem(self, cidadao):

        print(f"Enviando mensagem para o cidadão {cidadao['payload']['cidadao_nome']} no horário {cidadao['envio_horario_programado']}.")
        

"""if __name__ == "__main__":
    # Passo 1: Executar o fluxo de campanha (definir classificação e registrar cidadãos selecionados)
    disparador_service = EnvioMensagensService()
    # Disparos das 8h
    disparador_service.realizar_envio(
        envio_data='2025-03-31', 
        horario_envio='8h', 
        classificacao_experimento='teste',
        mensagem_tipo = 'mensagem_inicial'
        )
    # Disparos das 12h
    disparador_service.realizar_envio(
        envio_data='2025-03-31', 
        horario_envio='12h', 
        classificacao_experimento='teste',
        mensagem_tipo = 'mensagem_inicial'
        )
    # Disparos das 16h
    disparador_service.realizar_envio(
        envio_data='2025-03-31', 
        horario_envio='16h', 
        classificacao_experimento='teste',
        mensagem_tipo = 'mensagem_inicial'
        )"""
