from flask import Flask, request, jsonify
import psycopg2
from config import DATABASE

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(**DATABASE)
    return conn

@app.route('/notes', methods=['GET'])
def get_notes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content, created_at FROM m_notes;')
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{'id': note[0], 'title': note[1], 'content': note[2], 'created_at': note[3]} for note in notes])

@app.route('/notes', methods=['POST'])
def create_note():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO m_notes (title, content) VALUES (%s, %s) RETURNING id;', (title, content))
    note_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'id': note_id, 'title': title, 'content': content}), 201

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.json
    title = data.get('title')
    content = data.get('content')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE m_notes SET title = %s, content = %s WHERE id = %s;', (title, content, note_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Note updated'})

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM m_notes WHERE id = %s;', (note_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Note deleted'})

if __name__ == '__main__':
    app.run(debug=True)
