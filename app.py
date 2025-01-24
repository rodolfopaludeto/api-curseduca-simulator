from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurações das APIs da Curseduca
MEMBERS_API_URL = "https://prof.curseduca.pro"
GROUPS_API_URL = "https://clas.curseduca.pro"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoxNSwidXVpZCI6IjdjMGQ0OTk1LWRiZDQtMTFlZS1hYjFmLTEyYzhkMzIzN2I0ZiIsIm5hbWUiOiJSb2RvbGZvIFBhbHVkZXRvIiwiZW1haWwiOiJyb2RvbGZvcGFsdWRldG9AZ21haWwuY29tIiwiaW1hZ2UiOiJodHRwczovL2ZpbGVzLmN1cnNlZHVjYS5jb20vZjQ4ODRlNTUtN2Y1Zi00MGFlLTgxNGEtYTk5YTNjZmVmZWM5LzQ3OWFmMjRjOWYwYjEyNDYyNWU4MzFhYjMxNzljOTQxNGQ1ODY2MTIud2VicCIsInJvbGVzIjpbIkFETUlOIl0sInRlbmFudHMiOlsxLDZdfSwiaWF0IjoxNzM3MDM2OTU1LCJleHAiOjE3Mzk2Mjg5NTV9.jKleNAoBfxrc58Pb0aCxhO8jnEW6vDhuoF7FE0ICRUg"  # Substitua pelo token atualizado
API_KEY = "c0e968b5ed5d4c85accd7443ca3d105b07f1ce0d"  # Substitua pela chave de API
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
        if not data:
            return jsonify({"error": "Corpo da requisição vazio"}), 400

        nome = data.get("nome")
        email = data.get("email")

        if not nome or not email:
            return jsonify({"error": "Nome ou email não fornecidos"}), 400

        print(f"Recebendo dados do SpotForm: Nome={nome}, Email={email}")

        # Verificar se o usuário já existe
        membro = verificar_usuario(email)
        if not membro:
            print(f"Usuário não encontrado. Criando novo usuário para {email}...")
            membro = criar_usuario(nome, email)

        if not membro or "id" not in membro:
            print(f"Erro ao obter dados do membro. Resposta: {membro}")
            return jsonify({"error": "Falha ao criar ou encontrar usuário"}), 500

        print(f"Usuário encontrado ou criado: ID={membro['id']}")

        # Matricular o usuário na turma
        matricula = matricular_usuario_na_turma(membro["id"])
        if matricula.get("status") == "success":
            print("Usuário matriculado com sucesso.")
            return jsonify({"message": "Usuário matriculado com sucesso!"}), 200
        else:
            print(f"Erro na matrícula: {matricula.get('message')}")
            return jsonify({"error": "Falha ao matricular usuário na turma"}), 500

    except Exception as e:
        print("Erro inesperado no webhook:", str(e))
        return jsonify({"error": "Erro interno no servidor"}), 500

def verificar_usuario(email):
    """
    Verifica se o usuário já existe no LMS da Curseduca.
    """
    url = f"{CURSEDUCA_BASE_URL_MEMBERS}/members/by?email={email}"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()  # Retorna os dados do membro
        elif response.status_code == 404:
            print(f"Usuário com email {email} não encontrado.")
            return None
        else:
            print(f"Erro ao verificar usuário: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao verificar usuário: {e}")
        return None

def criar_usuario(nome, email):
    """
    Cria um novo usuário no LMS da Curseduca.
    """
    url = f"{CURSEDUCA_BASE_URL_MEMBERS}/register"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "name": nome,
        "email": email,
        "password": "sabergestao",
        "document": "12345678909",
        "phones": {
            "mobile": "(43) 99999-9999",
            "home": "(43) 3322-4455"
        },
        "sendConfirmationEmail": True,
        "birthDate": "2000-01-01T00:00:00Z",
        "address": {
            "zipCode": "86010-000",
            "street": "Rua Exemplo",
            "number": "123",
            "complement": "Apto 101",
            "city": "Londrina",
            "state": "PR"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            return response.json()["member"]  # Retorna os dados do membro criado
        else:
            print(f"Erro ao criar usuário: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao criar usuário: {e}")
        return None

def matricular_usuario_na_turma(membro_id):
    """
    Matricula o usuário em uma turma específica.
    """
    url = f"{CURSEDUCA_BASE_URL_GROUPS}/members/groups"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "member": {
            "id": membro_id
        },
        "group": {
            "id": TURMA_ID
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            return {"status": "success"}
        else:
            print(f"Erro ao matricular usuário: {response.text}")
            return {"status": "error", "message": response.text}
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao matricular usuário: {e}")
        return {"status": "error", "message": str(e)}

# Executar o aplicativo no servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
