from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurações da API da Curseduca
MEMBER_API_BASE_URL = "https://prof.curseduca.pro"  # Base URL para membros
CONTENT_API_BASE_URL = "https://clas.curseduca.pro"  # Base URL para conteúdos
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoxNSwidXVpZCI6IjdjMGQ0OTk1LWRiZDQtMTFlZS1hYjFmLTEyYzhkMzIzN2I0ZiIsIm5hbWUiOiJSb2RvbGZvIFBhbHVkZXRvIiwiZW1haWwiOiJyb2RvbGZvcGFsdWRldG9AZ21haWwuY29tIiwiaW1hZ2UiOiJodHRwczovL2ZpbGVzLmN1cnNlZHVjYS5jb20vZjQ4ODRlNTUtN2Y1Zi00MGFlLTgxNGEtYTk5YTNjZmVmZWM5LzQ3OWFmMjRjOWYwYjEyNDYyNWU4MzFhYjMxNzljOTQxNGQ1ODY2MTIud2VicCIsInJvbGVzIjpbXSwidGVuYW50cyI6WzEsNl19LCJpYXQiOjE3MzY0NjA1MzcsImV4cCI6MTczOTA1MjUzN30.QDEhjOgzaghZrfhGyL-hta1uXdW_i3gG3iJUUed95tA"  # Substitua pelo token JWT válido
API_KEY = "c0e968b5ed5d4c85accd7443ca3d105b07f1ce0d"  # Substitua pela sua API Key
TURMA_ID = 18  # ID da turma "Clientes Templum"

# Endpoint para verificar se o webhook está ativo
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Webhook ativo e funcionando!"})

# Endpoint que recebe o webhook do SpotForm
@app.route("/webhook", methods=["POST"])
def receber_webhook():
    """
    Recebe dados do SpotForm e processa a matrícula no LMS da Curseduca.
    """
    try:
        data = request.get_json()
        print("Dados recebidos:", data)

        if not data:
            return jsonify({"error": "Corpo da requisição vazio"}), 400

        nome = data.get("nome")
        email = data.get("email")

        if not nome or not email:
            return jsonify({"error": "Nome ou email não fornecidos"}), 400

        # Verifica se o usuário já existe no LMS
        user = verificar_usuario(email)

        if not user:
            print("Usuário não encontrado. Criando novo usuário...")
            user = criar_usuario(nome, email)

        if user:
            # Matricula o usuário na turma
            matricula = matricular_no_lms(email)
            if matricula.get("status") == "success":
                return jsonify({"message": "Matrícula realizada com sucesso!"}), 200
            else:
                print("Erro ao realizar matrícula:", matricula.get("message"))
                return jsonify({"error": "Falha ao realizar matrícula"}), 500

        return jsonify({"error": "Falha ao criar ou encontrar usuário"}), 500
    except Exception as e:
        print("Erro no processamento do webhook:", str(e))
        return jsonify({"error": "Erro interno no servidor"}), 500

def verificar_usuario(email):
    """
    Verifica se o usuário já existe no LMS da Curseduca.
    """
    url = f"{MEMBER_API_BASE_URL}/members/by?email={email}"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        user = response.json()
        print(f"Usuário encontrado: {user}")
        return user  # Retorna os detalhes do usuário encontrado
    except requests.exceptions.RequestException as e:
        print(f"Erro ao verificar usuário: {e}")
        return None

def criar_usuario(nome, email):
    """
    Cria um novo usuário no LMS da Curseduca.
    """
    url = f"{MEMBER_API_BASE_URL}/members"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "name": nome,
        "email": email
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code ao criar usuário: {response.status_code}")
        print(f"Resposta ao criar usuário: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao criar usuário: {e}")
        return None

def matricular_no_lms(email):
    """
    Realiza a matrícula do aluno no LMS da Curseduca.
    """
    url = f"{CONTENT_API_BASE_URL}/enrollments"
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
        print("Status Code da API:", response.status_code)
        print("Resposta da API:", response.text)

        response.raise_for_status()  # Lança erro se o status não for 2xx
        return {"status": "success", "data": response.json()}
    except requests.exceptions.RequestException as e:
        print(f"Erro ao integrar com a Curseduca: {e}")
        return {"status": "error", "message": str(e)}

# Executar o aplicativo no servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
