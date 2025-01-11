from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurações da API da Curseduca
CURSEDUCA_BASE_URL = "https://prof.curseduca.pro"
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
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição vazio"}), 400

    nome = data.get("nome")
    email = data.get("email")

    if not nome or not email:
        return jsonify({"error": "Nome ou email não fornecidos"}), 400

    # Realiza a matrícula no LMS da Curseduca
    matricula = matricular_no_lms(email)

    if matricula.get("status") == "success":
        return jsonify({"message": "Matrícula realizada com sucesso!"}), 200
    else:
        return jsonify({"error": "Falha ao realizar matrícula"}), 500

def matricular_no_lms(email):
    """
    Realiza a matrícula do aluno no LMS da Curseduca.
    """
    url = f"{CURSEDUCA_BASE_URL}/enrollments"
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
