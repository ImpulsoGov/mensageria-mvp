from datetime import datetime, timedelta
import random
from src.bd import BigQueryClient
from src.scripts.mvp_segunda_rodada.primeiro_disparo.utilitarios import TOKENS_MUNICIPIOS, USUARIOS_COLUNAS_TIPOS, EVENTOS_COLUNAS_TIPOS, MENSAGEM_TEMPLATE


class CampanhaService:
    def __init__(self):
        self.client = BigQueryClient()

    def executar_fluxo(self, municipio_id, campanha_nome,data_corrente):
        campanha = self.obter_campanha(campanha_nome)
        if not campanha or campanha['status'] != 'ativa':
            raise ValueError("Campanha inválida ou inativa")

        data_corrente_strp = datetime.strptime(data_corrente, '%Y-%m-%d').date()
        if data_corrente_strp < campanha['data_inicio']:
            raise ValueError("Campanha ainda não começou")

        data_fim = campanha['data_fim']
        dias_restantes = sum(1 for i in range((data_fim - data_corrente_strp).days + 1)
                     if (data_corrente_strp + timedelta(days=i)).weekday() < 5) 
                
        unidades = self.listar_unidades(municipio_id)

        for unidade in unidades:
            classificacao = self.listar_unidades_classificadas(unidade, campanha_nome)
            qtd_pessoas = max(1, unidade['total_pessoas'] // dias_restantes)
            pessoas = self.selecionar_pessoas(unidade['estabelecimento_saude_cnes'], qtd_pessoas)

            for pessoa in pessoas:
                self.registrar_cidadao_selecionado(pessoa, classificacao, data_corrente)

    def obter_campanha(self, campanha_nome):
        query = f"""
            SELECT * FROM `ip_mensageria_camada_ouro.campanhas`
            WHERE campanha_nome = '{campanha_nome}'
            LIMIT 1
        """
        campanha_df = self.client.consultar_dados(query)
        return campanha_df.iloc[0].to_dict() if not campanha_df.empty else None

    def listar_unidades(self, municipio_id):
        query = f"""
            SELECT estabelecimento_saude_cnes, COUNT(cidadao_id) AS total_pessoas
            FROM `ip_mensageria_camada_ouro.cidadao_elegivel`
            WHERE municipio_id_sus = '{municipio_id}'
            GROUP BY estabelecimento_saude_cnes
        """
        unidades_df = self.client.consultar_dados(query)
        return unidades_df.to_dict(orient="records")
    
    def listar_unidades_classificadas(self, unidade, campanha_nome):
        # Consultar se a unidade já está classificada
        query = f"""
            SELECT classificacao_experimento
            FROM `predictive-keep-314223.ip_mensageria_camada_ouro.estabelecimento_scnes_classificados`
            WHERE estabelecimento_saude_cnes = '{unidade.get('estabelecimento_saude_cnes')}'
            AND campanha_nome = '{campanha_nome}'
            LIMIT 1
        """
        
        # Verificar se a consulta retorna algum valor
        classificacao_df = self.client.consultar_dados(query)
        
        if not classificacao_df.empty:
            # Se já está classificado, retornar a classificação existente
            return classificacao_df.iloc[0]['classificacao_experimento']
        
        # Se não estiver classificado, chama o método para definir e registrar a classificação
        return self.definir_classificacao_unidade(unidade, campanha_nome)

    def definir_classificacao_unidade(self, unidade, campanha):

        classificacao_experimento = random.choice(["controle", "teste"])
        unidade_classificada = {
            'estabelecimento_saude_cnes':  str(unidade.get('estabelecimento_saude_cnes')),
            'campanha_nome': str(campanha),
            'classificacao_experimento': str(classificacao_experimento)
        }
        tabela = 'predictive-keep-314223.ip_mensageria_camada_ouro.estabelecimento_scnes_classificados'

        self.client.inserir_dados(tabela, [unidade_classificada])
        return classificacao_experimento

    def selecionar_pessoas(self, estabelecimento_saude_cnes, qtd_pessoas):
        query = f"""
            SELECT * FROM `ip_mensageria_camada_ouro.cidadao_elegivel`
            WHERE estabelecimento_saude_cnes = '{estabelecimento_saude_cnes}'
            LIMIT {qtd_pessoas}
        """
        pessoas_df = self.client.consultar_dados(query)
        return pessoas_df.to_dict(orient="records")
    
    def definir_classificacao_experimento(self, classificacao):
        """Define a classificação do experimento para o cidadão."""
        return classificacao

    def definir_horario_envio(self):
        """Define aleatoriamente o horário de envio da mensagem."""
        return random.choice(["8h", "12h", "16h"])

    def definir_mensagem_template_id(self):
        """Seleciona aleatoriamente um ID de template de mensagem."""
        return random.randint(1, 9)
    
    def definir_mensagem_linha_cuidado(self, linha_cuidado):
        """Ajusta o valor da linha de cuidado conforme regras de categorização."""
        if linha_cuidado in ["diabeticos", "hipertensos", "hipertensos_diabeticos"]:
            return "cronicos"
        return linha_cuidado
    
    def definir_mensagem_template_nome(self, mensagem_linha_cuidado, mensagem_template_id):
        """Define o nome do template da mensagem com base nas regras."""
        if mensagem_linha_cuidado in MENSAGEM_TEMPLATE and mensagem_template_id in MENSAGEM_TEMPLATE[mensagem_linha_cuidado]:
            template_tipo, versao, _, _ = MENSAGEM_TEMPLATE[mensagem_linha_cuidado][mensagem_template_id]
            return f'mensageria_usuarios_{mensagem_linha_cuidado}_{template_tipo}_{versao}'
        return None  # Retorna None caso não haja template correspondente

    def definir_mensagem_midia_link(self, mensagem_linha_cuidado, mensagem_template_id, municipio_id_sus):
        """Define o link de mídia da mensagem com base nas regras."""
        if mensagem_linha_cuidado in MENSAGEM_TEMPLATE and mensagem_template_id in MENSAGEM_TEMPLATE[mensagem_linha_cuidado]:
            template_tipo, _, _, link_func = MENSAGEM_TEMPLATE[mensagem_linha_cuidado][mensagem_template_id]
            return (
                link_func(municipio_id_sus=municipio_id_sus, template_tipo=template_tipo, linha_cuidado=mensagem_linha_cuidado)
                if callable(link_func)
                else link_func
            )
        return None  # Retorna None caso não haja link correspondente

    def registrar_cidadao_selecionado(self, pessoa, classificacao, data_corrente:str):

        municipio_id_sus = pessoa['municipio_id_sus']
        mensagem_linha_cuidado = self.definir_mensagem_linha_cuidado(pessoa['linha_cuidado'])
        mensagem_template_id = self.definir_mensagem_template_id()
        
        pessoa['classificacao_experimento'] = self.definir_classificacao_experimento(classificacao)
        pessoa['envio_data_programado'] = str(data_corrente)  # Adicionando a data do envio
        pessoa['envio_horario_programado'] = self.definir_horario_envio()
        pessoa['mensagem_template_cod'] = mensagem_template_id
        pessoa['mensagem_template'] = self.definir_mensagem_template_nome(mensagem_linha_cuidado, mensagem_template_id)
        pessoa['mensagem_midia_link'] = self.definir_mensagem_midia_link(mensagem_linha_cuidado, mensagem_template_id,municipio_id_sus)

        pessoa['payload']['cidadao_dt_nascimento'] = str(pessoa['payload']['cidadao_dt_nascimento'].strftime('%Y-%m-%d'))

        # Consultar se o cidadao_id para campanha_nome já existem na tabela
        query = f"""
            SELECT COUNT(*) 
            FROM `ip_mensageria_camada_ouro.cidadao_selecionado`
            WHERE cidadao_id = '{pessoa['cidadao_id']}' AND campanha_nome = '{pessoa['campanha_nome']}'
        """
        resultado = self.client.consultar_dados(query)

        # Se o registro não existe (count é 0), faz a inserção
        if resultado.iloc[0, 0] == 0:
            tabela = 'predictive-keep-314223.ip_mensageria_camada_ouro.cidadao_selecionado'
            self.client.inserir_dados(tabela, [pessoa])
            print("Pessoa inserida com sucesso")
        else:
            print("Registro já existe, não inserido.")


#if __name__ == "__main__":
    # Passo 1: Executar o fluxo de campanha (definir classificação e registrar cidadãos selecionados)
    #campanha_service = CampanhaService()
    # Para cada municipio:
    #campanha_service.executar_fluxo(municipio_id="210535", campanha_nome="mvp_ciclo2",data_corrente='2025-03-31')