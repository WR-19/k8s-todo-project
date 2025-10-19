from flask import Flask, jsonify
app = Flask(__name__)

todos = []

@app.route('/')
def hello():
    return "🚀 Kubernetes Todo API is LIVE! ✅"

@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
