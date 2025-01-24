from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurações das APIs da Curseduca
MEMBERS_API_URL = "https://prof.curseduca.pro"
GROUPS_API_URL = "https://clas.curseduca.pro"
AUTH_TOKEN = "Bearer <SEU_ACCESS_TOKEN>"  # Substitua pelo token atualizado
API_KEY = "<SUA_API_KEY>"  # Substitua pela chave de API
TURMA_ID = 18  # ID da turma "Clientes Templum"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Webhook ativo e funcionando!"})

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

    # Verificar se o usuário já existe
    membro = verificar_usuario(email)
    if not membro:
        # Criar novo usuário
        membro = criar_usuario(nome, email)
        if not membro:
            return jsonify({"error": "Falha ao criar usuário"}), 500

    # Matricular usuário na turma
    matricula = matricular_usuario_na_turma(membro["id"], membro["uuid"])
    if matricula:
        return jsonify({"message": "Usuário matriculado com sucesso!"}), 200
    else:
        return jsonify({"error": "Falha ao matricular usuário"}), 500

def verificar_usuario(email):
    """
    Verifica se o usuário já existe no Saber Play.
    """
    url = f"{MEMBERS_API_URL}/members/by?email={email}"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao verificar usuário: {e}")
        return None

def criar_usuario(nome, email):
    """
    Cria um novo usuário no Saber Play.
    """
    url = f"{MEMBERS_API_URL}/register"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "name": nome,
        "email": email,
        "password": "sabergestao",
        "document": "12345678909",  # CPF fictício
        "phones": {"mobile": "(43) 99999-9999"},
        "sendConfirmationEmail": True,
        "birthDate": "2005-01-01T00:00:00Z",
        "address": {
            "zipCode": "12345678",
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
            return response.json()
        else:
            print(f"Erro ao criar usuário: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao criar usuário: {e}")
        return None

def matricular_usuario_na_turma(member_id, member_uuid):
    """
    Matricula o usuário na turma configurada.
    """
    url = f"{MEMBERS_API_URL}/members/groups"
    headers = {
        "Authorization": AUTH_TOKEN,
        "api_key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "member": {
            "id": member_id,
            "uuid": member_uuid,
            "role": "STUDENT"
        },
        "groups": [str(TURMA_ID)],
        "customExpirationDate": "2025-12-31T23:59:59Z"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Erro ao matricular usuário: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Erro ao matricular usuário: {e}")
        return False

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
