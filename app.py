from dotenv import load_dotenv
from flask import Flask, request, jsonify
from google.cloud import secretmanager
import json
import os
# Carrega as variáveis de ambiente
load_dotenv()

# Importando as funções
from src.scripts.passo_1_selecao_cidadao import selecionar_cidadaos
from src.scripts.passo_2_match_com_equipe_e_upload_turn import processo_envio_turn
from src.scripts.passo_3_envio_de_mensagens import programa_mensagens
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

@app.route("/passo1", methods=['GET'])
def passo1():
    try:
        # Validação da chave recebida
        chave_recebida = request.headers.get("X-API-Key")
        logger.info("Autenticando chave de acesso")
        validar_autenticacao(chave_recebida=chave_recebida)
        # Se a chave não for fornecida, retornar erro
        if not chave_recebida:
            return jsonify({"error": "Chave de API ausente"}), 401
        # Autenticar a requisição
        if not validar_autenticacao(chave_recebida=chave_recebida):
            return jsonify({"error": "Chave de API inválida"}), 401
        logger.info("Processo iniciado")
        resultado = selecionar_cidadaos()
        if resultado["status"] == "sucesso":
            logger.info("Processo finalizado")
    except Exception as e:
        logger.error(f"Extração falhou. Exceção: {e}")
        return jsonify({f"erro": f"Erro do servidor: {str(e)}"}), 500

@app.route("/passo2", methods=['GET'])
def passo2():
    try:
        # Validação da chave recebida
        chave_recebida = request.headers.get("X-API-Key")
        logger.info("Autenticando chave de acesso")
        validar_autenticacao(chave_recebida=chave_recebida)
        # Se a chave não for fornecida, retornar erro
        if not chave_recebida:
            return jsonify({"error": "Chave de API ausente"}), 401
        # Autenticar a requisição
        if not validar_autenticacao(chave_recebida=chave_recebida):
            return jsonify({"error": "Chave de API inválida"}), 401
        logger.info("Processo iniciado")
        resultado = processo_envio_turn()
        if resultado["status"] == "sucesso":
            logger.info("Processo finalizado")
    except Exception as e:
        logger.error(f"Extração falhou. Exceção: {e}")
        return jsonify({f"erro": f"Erro do servidor: {str(e)}"}), 500

@app.route("/passo3", methods=['GET'])
def passo3():
    try:
        # Validação da chave recebida
        chave_recebida = request.headers.get("X-API-Key")
        logger.info("Autenticando chave de acesso")
        validar_autenticacao(chave_recebida=chave_recebida)
        # Se a chave não for fornecida, retornar erro
        if not chave_recebida:
            return jsonify({"error": "Chave de API ausente"}), 401
        # Autenticar a requisição
        if not validar_autenticacao(chave_recebida=chave_recebida):
            return jsonify({"error": "Chave de API inválida"}), 401
        logger.info("Processo iniciado")
        resultado = programa_mensagens()
        if resultado["status"] == "sucesso":
            logger.info("Processo finalizado")
    except Exception as e:
        logger.error(f"Extração falhou. Exceção: {e}")
        return jsonify({f"erro": f"Erro do servidor: {str(e)}"}), 500


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
