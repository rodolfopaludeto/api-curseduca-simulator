from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint de matrícula (simulado)
@app.route('/enrollments', methods=['POST'])
def create_enrollment():
    data = request.json
    member = data.get("member", {})
    content_id = data.get("contentId")

    # Resposta simulada
    return jsonify({
        "status": "success",
        "message": "Matrícula criada com sucesso!",
        "member": member,
        "contentId": content_id
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

