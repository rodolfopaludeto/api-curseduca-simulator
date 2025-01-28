from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurações das APIs da Curseduca
BASE_URL = "https://prof.curseduca.pro"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
API_KEY = "c0e968b5ed5d4c85accd7443ca3d105b07f1ce0d"
TURMA_ID = 18  # ID da turma "Clientes Templum"

# Endpoint para verificar se o webhook está ativo
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Webhook ativo e funcionando!"})

# Endpoint que recebe o webhook do SpotForm
@app.route("/webhook", methods=["POST"])
def receber_webhook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição vazio"}), 400

        # 🔍 Verifica onde estão os dados e os extrai corretamente
        content = data.get("content", {})
        nome = content.get("Campo de Texto")  # Nome do campo no SpotForm
        email = content.get("Campo de E-mail")  # Nome do campo no SpotForm

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

# Funções para verificar usuário, criar usuário e matricular
def verificar_usuario(email):
    url = f"{BASE_URL}/members/by?email={email}"
    headers = {"Authorization": AUTH_TOKEN, "api_key": API_KEY}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

def criar_usuario(nome, email):
    url = f"{BASE_URL}/register"
    headers = {"Authorization": AUTH_TOKEN, "api_key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "name": nome,
        "email": email,
        "password": "sabergestao",
        "document": "12345678909",
        "phones": {"mobile": "(43) 99999-9999", "home": "(43) 3322-4455"},
        "sendConfirmationEmail": True,
        "birthDate": "2000-01-01T00:00:00Z",
        "address": {"zipCode": "86010-000", "street": "Rua Exemplo", "number": "123", "complement": "Apto 101", "city": "Londrina", "state": "PR"}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()["member"] if response.status_code == 201 else None

def matricular_usuario_na_turma(membro_id):
    url = f"{BASE_URL}/members/groups"
    headers = {"Authorization": AUTH_TOKEN, "api_key": API_KEY, "Content-Type": "application/json"}
    payload = {"member": {"id": membro_id, "role": "STUDENT"}, "group": {"id": TURMA_ID}}
    response = requests.post(url, json=payload, headers=headers)
    return {"status": "success"} if response.status_code in [200, 201] else {"status": "error", "message": response.text}

# Executar o aplicativo no servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
