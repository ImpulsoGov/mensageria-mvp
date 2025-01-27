from dotenv import load_dotenv
from flask import Flask, request, jsonify
from google.cloud import secretmanager
import json
import os
# Carrega as variáveis de ambiente
load_dotenv()

# Importando as funções
from src.scripts.segundo_ciclo.enviar_mensagens import processar_envios
from src.loggers import logger

PROJECT_ID = os.getenv('PROJECT_ID')

if not PROJECT_ID:
    raise ValueError("A variável de ambiente 'PROJECT_ID' não está definida")

app = Flask(__name__)

def validar_autenticacao(
        chave_recebida: str,
        projeto_id="567502497958",
        versao="latest",
        secret_id="mensageria-chave-api",
    ):
    # Obter o valor da chave secreta do Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    # Constrói o nome do recurso da versão do segredo
    name = f"projects/{projeto_id}/secrets/{secret_id}/versions/{versao}"
    # Acessa o segredo
    response = client.access_secret_version(name=name)
    chave_secreta = response.payload.data.decode("UTF-8")
    # Comparar a chave recebida com a chave secreta
    if chave_recebida != chave_secreta:
        return False
    return True

@app.route("/enviar_mensagens", methods=['POST'])
def enviar_mensagens():
    try:
        # Validação da chave recebida
        chave_recebida = request.headers.get("X-API-Key")
        logger.info("Autenticando chave de acesso")
        
        if not chave_recebida:
            return jsonify({"error": "Chave de API ausente"}), 401
        
        # Autenticar a requisição
        if not validar_autenticacao(chave_recebida=chave_recebida):
            return jsonify({"error": "Chave de API inválida"}), 401
        
        # Extração do payload JSON
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "Payload ausente ou inválido"}), 400
        
        municipio_id_sus = payload.get("municipio_id_sus")
        data_programada = payload.get("data_programada")
        
        if not municipio_id_sus or not data_programada:
            return jsonify({"error": "Os campos 'municipio_id_sus' e 'data_programada' são obrigatórios"}), 400
        
        logger.info(f"Processo iniciado para município: {municipio_id_sus} e data: {data_programada}")
        
        # Chama a função de processamento com os parâmetros fornecidos
        resultado = processar_envios(
            municipio_id_sus=municipio_id_sus, 
            data_programada=data_programada
            )
        
        if resultado.get("status") == 200:
            logger.info("Processo finalizado com sucesso")
            return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"Extração falhou. Exceção: {e}")
        return jsonify({f"erro": f"Erro do servidor: {str(e)}"}), 500



if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
