from flask import Flask, jsonify, request
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'todo_db'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'password123'),
        port=os.getenv('DB_PORT', '5432')
    )
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def hello():
    return """
    <h1>🚀 Kubernetes Todo App</h1>
    <p><strong>Full CRUD API with PostgreSQL</strong></p>
    <p><strong>Endpoints:</strong></p>
    <ul>
        <li>GET /todos - List all todos</li>
        <li>POST /todos - Create new todo</li>
        <li>PUT /todos/{id} - Update todo</li>
        <li>DELETE /todos/{id} - Delete todo</li>
    </ul>
    """

@app.route('/todos', methods=['GET'])
def get_todos():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM todos ORDER BY created_at DESC;')
        todos = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([dict(todo) for todo in todos])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/todos', methods=['POST'])
def create_todo():
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({"error": "Title is required"}), 400
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            'INSERT INTO todos (title) VALUES (%s) RETURNING *;',
            (title,)
        )
        new_todo = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify(dict(new_todo)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        data = request.get_json()
        title = data.get('title')
        completed = data.get('completed')
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if title is not None and completed is not None:
            cur.execute(
                'UPDATE todos SET title = %s, completed = %s WHERE id = %s RETURNING *;',
                (title, completed, todo_id)
            )
        elif title is not None:
            cur.execute(
                'UPDATE todos SET title = %s WHERE id = %s RETURNING *;',
                (title, todo_id)
            )
        elif completed is not None:
            cur.execute(
                'UPDATE todos SET completed = %s WHERE id = %s RETURNING *;',
                (completed, todo_id)
            )
        else:
            return jsonify({"error": "No fields to update"}), 400
        
        updated_todo = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if not updated_todo:
            return jsonify({"error": "Todo not found"}), 404
        
        return jsonify(dict(updated_todo))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('DELETE FROM todos WHERE id = %s RETURNING *;', (todo_id,))
        deleted_todo = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if not deleted_todo:
            return jsonify({"error": "Todo not found"}), 404
        
        return jsonify({"message": "Todo deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
