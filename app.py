from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db_user= os.getenv('DB_USER')
db_pass= os.getenv('DB_PASS')
db_host= os.getenv('DB_HOST')
db_port= os.getenv('DB_PORT')
db_name= os.getenv('DB_NAME')
origin_1= os.getenv('ORIGIN_1')
origin_2= os.getenv('ORIGIN_2')

def get_db_connection():
    try:
        connectionStr = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        conn = psycopg2.connect(connectionStr)
        return conn
    except psycopg2.Error as e:
        return e

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
