from flask import Flask, request, jsonify
from urllib.parse import quote as url_quote  # Substituição do url_quote

app = Flask(__name__)

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

# Rota de exemplo para simular matrículas
@app.route("/enrollments", methods=["POST"])
def enrollments():
    """
    Rota para criar uma matrícula.
    Espera um JSON no corpo da requisição com os campos:
    {
        "member": {
            "id": 1,
            "email": "email@example.com"
        },
        "contentId": 123
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição vazio"}), 400

    member = data.get("member")
    content_id = data.get("contentId")

    if not member or not content_id:
        return jsonify({"error": "Dados incompletos"}), 400

    # Simulação de sucesso na matrícula
    return jsonify({
        "message": "Matrícula criada com sucesso!",
        "member": member,
        "contentId": content_id
    }), 201

# Executar o aplicativo no servidor local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

