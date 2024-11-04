from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from config import DATABASE

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://subtle-capybara-f5d487.netlify.app/"]}})

def get_db_connection():
    conn = psycopg2.connect(**DATABASE)
    return conn

@app.route('/get-notes', methods=['GET'])
def get_notes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT id, content, color, updated_at FROM m_notes WHERE deleted_at is null;''')
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{'id': note[0], 'content': note[1], 'color': note[2], 'updated_at': note[3]} for note in notes])

@app.route('/add-note', methods=['POST'])
def create_note():
    data = request.json
    content = data.get('content')
    color = data.get('color')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO m_notes (content, color) VALUES (%s, %s) RETURNING id;', (content, color))
    note_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'id': note_id, 'color': color, 'content': content}), 201

@app.route('/update-note', methods=['POST'])
def update_note():
    data = request.json
    id = data.get('id')
    content = data.get('content')
    color = data.get('color')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE m_notes SET content = %s, color = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s and deleted_at is null;', (content, color, id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Note updated'})

@app.route('/delete-note', methods=['POST'])
def delete_note():
    data = request.json
    id = data.get('id')
    print("this is id ",id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE m_notes SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s;', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Note deleted'})

if __name__ == '__main__':
    app.run(debug=True)
