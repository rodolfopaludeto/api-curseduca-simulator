from flask import Flask, request, jsonify
from urllib.parse import quote as url_quote  # Substituição do url_quote
import requests

app = Flask(__name__)

# Configurações para a API do Saber Play
SABER_PLAY_API_BASE_URL = "https://api.curseduca.com"  # Substitua pela URL real da API
SABER_PLAY_API_TOKEN = "seu-token-aqui"  # Substitua pelo token da API

# Rota inicial para verificar se o servidor está funcionando
@app.route("/")
def home():
    return jsonify({"message": "API está funcionando!"})

# Exemplo de rota que utiliza url_quote
@app.route("/encode", methods=["GET"])
def encode_url():
    """
    Rota que recebe um parâmetro 'text' e retorna o texto codificado em URL.
    Exemplo: /encode?text=Olá Mundo!
    """
    text = request.args.get("text", "")
    encoded_text = url_quote(text)  # Codifica o texto usando urllib.parse.quote
    return jsonify({"encoded_text": encoded_text})

# Rota para receber dados do SPOTFORM e matricular no Saber Play
@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Endpoint para receber dados do SPOTFORM via webhook.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição vazio"}), 400

    nome = data.get("nome")
    email = data.get("email")

    if not nome or not email:
        return jsonify({"error": "Nome ou email não fornecidos"}), 400

    # Exemplo de ID da turma para matrícula
    turma_id = 123

    # Chamada à função para matricular no Saber Play
    matricula = matricular_no_saberplay(email, turma_id)

    if matricula.get("status") == "success":
        return jsonify({"message": "Matrícula enviada ao Saber Play com sucesso!"}), 200
    else:
        return jsonify({"error": "Falha ao enviar matrícula ao Saber Play"}), 500

# Função para integrar com o Saber Play
def matricular_no_saberplay(email, turma_id):
    """
    Faz a matrícula do aluno no Saber Play usando a API da Curseduca.
    """
    headers = {
        "Authorization": f"Bearer {SABER_PLAY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "member": {
            "email": email
        },
        "contentId": turma_id
    }

    try:
        response = requests.post(f"{SABER_PLAY_API_BASE_URL}/enrollments", json=payload, headers=headers)
        response.raise_for_status()  # Lança erro se o status não for 2xx
        return response.json()  # Retorna a resposta da API
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Executar o aplicativo no servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
