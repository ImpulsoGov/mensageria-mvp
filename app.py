import os
import datetime

from flask import Flask, request, jsonify


from src.scripts.passo_1_selecao_cidadao import processa_passo_1

app = Flask(__name__)


@app.route("/passo_1", methods=['POST'])
def passo_1():
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return 'Erro, content-type deve ser json', 400


    return processa_passo_1()


#@app.route("/passo_2", methods=['POST'])

#@app.route("/passo_3", methods=['POST'])

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))