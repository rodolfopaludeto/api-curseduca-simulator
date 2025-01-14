from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurações da API da Curseduca
CURSEDUCA_MEMBERS_URL = "https://prof.curseduca.pro"
CURSEDUCA_CONTENTS_URL = "https://clas.curseduca.pro"
API_KEY = "c0e968b5ed5d4c85accd7443ca3d105b07f1ce0d"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoxNSwidXVpZCI6IjdjMGQ0OTk1LWRiZDQtMTFlZS1hYjFmLTEyYzhkMzIzN2I0ZiIsIm5hbWUiOiJSb2RvbGZvIFBhbHVkZXRvIiwiZW1haWwiOiJyb2RvbGZvcGFsdWRldG9AZ21haWwuY29tIiwiaW1hZ2UiOiJodHRwczovL2ZpbGVzLmN1cnNlZHVjYS5jb20vZjQ4ODRlNTUtN2Y1Zi00MGFlLTgxNGEtYTk5YTNjZmVmZWM5LzQ3OWFmMjRjOWYwYjEyNDYyNWU4MzFhYjMxNzljOTQxNGQ1ODY2MTIud2VicCIsInJvbGVzIjpbXSwidGVuYW50cyI6WzEsNl19LCJpYXQiOjE3MzY4ODExMDksImV4cCI6MTczOTQ3MzEwOX0.GP4kRsq-piaaosvn9zPfEhI76ddce-kRtlNbb3dy218"
REFRESH_TOKEN = "9fe0c1de-32d2-483d-ba5d-19bd66ae7f97"
TURMA_ID = 18  # ID da turma "Clientes Templum"

# Função para renovar o token de acesso
def renovar_token():
    url = f"{CURSEDUCA_MEMBERS_URL}/refresh"
    headers = {
        "Content-Type": "application/json",
        "api_key": API_KEY
    }
    payload = {
        "refreshToken": REFRESH_TOKEN
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        novo_token = response.json().get("accessToken")
        return f"Bearer {novo_token}"
    except requests.exceptions.RequestException as e:
        print(f"Erro ao renovar token: {e}")
        return None

# Middleware para verificar e renovar o token antes das requisições
def verificar_ou_renovar_token():
    global AUTH_TOKEN
    # Aqui você pode implementar uma lógica para verificar se o token expirou
    # ou simplesmente renovar o token sempre que esta função for chamada
    novo_token = renovar_token()
    if novo_token:
        AUTH_TOKEN = novo_token

# Endpoint para verificar se o webhook está ativo
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Webhook ativo e funcionando!"})

# Endpoint que recebe o webhook do SpotForm
@app.route("/webhook", methods=["POST"])
def receber_webhook():
    verificar_ou_renovar_token()

    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição vazio"}), 400

    nome = data.get("nome")
    email = data.get("email")

    if not nome or not email:
        return jsonify({"error": "Nome ou email não fornecidos"}), 400

    # Verifica ou cria o usuário
    usuario = verificar_ou_criar_usuario(email, nome)
    if not usuario:
        return jsonify({"error": "Falha ao criar ou encontrar usuário"}), 500

    # Matricula o usuário na turma
    matricula = matricular_no_lms(email)
    if matricula.get("status") == "success":
        return jsonify({"message": "Matrícula realizada com sucesso!"}), 200
    else:
        return jsonify({"error": "Falha ao realizar matrícula"}), 500

# Função para verificar ou criar usuário no LMS
def verificar_ou_criar_usuario(email, nome):
    url = f"{CURSEDUCA_MEMBERS_URL}/members/by?email={email}"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY
    }

    try:
        # Tenta buscar o usuário
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()

        # Se o usuário não existe, cria um novo
        url = f"{CURSEDUCA_MEMBERS_URL}/members"
        payload = {
            "email": email,
            "name": nome
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Erro ao verificar ou criar usuário: {e}")
        return None

# Função para matricular usuário no LMS
def matricular_no_lms(email):
    url = f"{CURSEDUCA_CONTENTS_URL}/enrollments"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "member": {"email": email},
        "contentId": TURMA_ID
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.RequestException as e:
        print(f"Erro ao integrar com a Curseduca: {e}")
        return {"status": "error", "message": str(e)}

# Executar o aplicativo no servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
