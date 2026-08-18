from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from voice_assistant import VoiceAssistant
import datetime
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
assistant = VoiceAssistant(name="Aria")

@app.route('/')
def index():
    return render_template('index.html', assistant_name=assistant.name)

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/presentation')
def presentation():
    """Interactive HTML Slide Presentation Deck."""
    return render_template('presentation.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system and assistant status info."""
    return jsonify({
        "status": "online",
        "name": assistant.name,
        "mic_available": assistant.microphone_available,
        "pyttsx3_available": assistant.tts_engine is not None,
        "current_time": datetime.datetime.now().strftime("%I:%M:%S %p"),
        "current_date": datetime.datetime.now().strftime("%A, %B %d, %Y"),
        "system_stats": assistant.get_system_stats()
    })

@app.route('/api/command', methods=['POST'])
def handle_command():
    """Process incoming voice or text command."""
    data = request.json or {}
    user_command = data.get("command", "").strip()
    speak_audio = data.get("speak", True)
    
    if not user_command:
        return jsonify({"error": "No command provided"}), 400

    response_text, action_type, extra_details = assistant.process_command(user_command)
    
    # Speak out response out loud on server
    if speak_audio:
        try:
            assistant.speak(response_text)
        except Exception as e:
            print(f"[TTS Server Error] {e}")

    return jsonify({
        "status": "success",
        "command": user_command,
        "response": response_text,
        "action": action_type,
        "details": extra_details,
        "timestamp": datetime.datetime.now().strftime("%I:%M:%S %p")
    })

@app.route('/api/listen', methods=['POST'])
def trigger_listen():
    """Trigger server-side microphone listening."""
    if not assistant.microphone_available:
        return jsonify({
            "status": "warning",
            "message": "Microphone hardware not available on server host. Please use browser speech recognition or text input."
        })
    
    command = assistant.listen(timeout=4)
    if command:
        response_text, action_type, extra_details = assistant.process_command(command)
        return jsonify({
            "status": "success",
            "command": command,
            "response": response_text,
            "action": action_type,
            "details": extra_details,
            "timestamp": datetime.datetime.now().strftime("%I:%M:%S %p")
        })
    else:
        return jsonify({
            "status": "error",
            "message": "No clear speech detected. Please try speaking again."
        })

# --------------------------------------------------
# Database Initialization (SQLite - Persistent SQL Database)
# --------------------------------------------------
import sqlite3
import uuid
import time
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            provider TEXT NOT NULL,
            picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            category TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check for missing columns in existing table (graceful schema migration)
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    if 'password_hash' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if 'picture' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN picture TEXT")
    if 'last_login' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
    conn.commit()
    conn.close()

init_db()

def get_or_create_derived_user_id(cursor, provider, email=None):
    """
    Generates or retrieves a derived user ID starting from 1 for each provider
    e.g. google_user_1, google_user_2, email_user_1, github_user_1, etc.
    """
    if email:
        cursor.execute('SELECT id FROM users WHERE LOWER(email) = LOWER(?)', (email.strip().lower(),))
        row = cursor.fetchone()
        if row and row[0]:
            return row[0]
    
    clean_provider = provider.lower().replace(' ', '_').replace('id', '').strip('_')
    if not clean_provider:
        clean_provider = 'user'
        
    cursor.execute('SELECT COUNT(*) FROM users WHERE LOWER(provider) = LOWER(?)', (provider.strip().lower(),))
    count = cursor.fetchone()[0]
    next_num = count + 1
    return f"{clean_provider}_user_{next_num}"

@app.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip() or email.split('@')[0].capitalize()

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

    if len(password) < 6:
        return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters long'}), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE LOWER(email) = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'status': 'error', 'message': 'An account with this email already exists'}), 400

        provider = 'Email'
        user_id = get_or_create_derived_user_id(cursor, provider, email)
        password_hash = generate_password_hash(password)

        cursor.execute('''
            INSERT INTO users (id, name, email, password_hash, provider, picture)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, email, password_hash, provider, ''))
        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Account registered successfully',
            'user': {
                'id': user_id,
                'name': name,
                'email': email,
                'provider': provider,
                'picture': ''
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500

@app.route('/api/auth/email-login', methods=['POST'])
def api_auth_email_login():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, password_hash, provider, picture FROM users WHERE LOWER(email) = ?', (email,))
        user_row = cursor.fetchone()

        if not user_row:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

        user_id, name, user_email, db_pwd_hash, provider, picture = user_row

        if db_pwd_hash and not check_password_hash(db_pwd_hash, password):
            conn.close()
            return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'user': {
                'id': user_id,
                'name': name,
                'email': user_email,
                'provider': provider,
                'picture': picture or ''
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500

@app.route('/api/auth/google', methods=['POST'])
def api_auth_google():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip() or (email.split('@')[0].capitalize() if email else 'Google User')
    google_id = data.get('google_id') or data.get('sub') or f"g_{int(time.time())}"
    picture = data.get('picture', '')
    provider = 'Google'

    if not email:
        email = f"google_{google_id[:8]}@gmail.com"

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name FROM users WHERE LOWER(email) = ?', (email,))
        row = cursor.fetchone()

        if row:
            user_id = row[0]
            cursor.execute('''
                UPDATE users SET name = ?, provider = ?, picture = ?, last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (name, provider, picture, user_id))
        else:
            user_id = get_or_create_derived_user_id(cursor, provider, email)
            cursor.execute('''
                INSERT INTO users (id, name, email, provider, picture)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, email, provider, picture))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'user': {
                'id': user_id,
                'name': name,
                'email': email,
                'provider': provider,
                'picture': picture
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Google Auth DB Error: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    data = request.json or {}
    provider = data.get('provider', 'Email').strip()
    email = data.get('email', 'user@example.com').strip().lower()
    name = data.get('name', email.split('@')[0].capitalize())

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        user_id = get_or_create_derived_user_id(cursor, provider, email)
        
        cursor.execute('''
            INSERT INTO users (id, name, email, provider) VALUES (?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET name = excluded.name, provider = excluded.provider, last_login = CURRENT_TIMESTAMP
        ''', (user_id, name, email, provider))
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB user save notice:", e)
        user_id = f"{provider.lower()}_user_1"

    return jsonify({
        'status': 'success',
        'user': {
            'id': user_id,
            'name': name,
            'email': email,
            'provider': provider
        }
    })

@app.route('/api/db/user', methods=['POST'])
def api_db_user():
    data = request.json or {}
    provider = data.get('provider', 'Guest').strip()
    email = data.get('email', 'guest@aria.ai').strip().lower()
    name = data.get('name', 'Guest')
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        user_id = get_or_create_derived_user_id(cursor, provider, email)
        
        cursor.execute('''
            INSERT INTO users (id, name, email, provider) VALUES (?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET name = excluded.name, provider = excluded.provider, last_login = CURRENT_TIMESTAMP
        ''', (user_id, name, email, provider))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'user': {'id': user_id, 'name': name, 'email': email, 'provider': provider}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/db/history', methods=['GET', 'POST', 'DELETE'])
def api_db_history():
    user_id = request.args.get('user_id', 'guest_user_1')
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.json or {}
        session_id = data.get('session_id', 'session_default')
        role = data.get('role', 'user')
        message = data.get('message', '')
        category = data.get('category', 'general')
        cursor.execute('INSERT INTO chat_history (user_id, session_id, role, message, category) VALUES (?, ?, ?, ?, ?)',
                       (user_id, session_id, role, message, category))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})

    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'History cleared'})

    else:
        cursor.execute('SELECT session_id, role, message, category, timestamp FROM chat_history WHERE user_id = ? ORDER BY id ASC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        messages = [{'session_id': r[0], 'role': r[1], 'message': r[2], 'category': r[3], 'timestamp': r[4]} for r in rows]
        return jsonify({'status': 'success', 'history': messages})

@app.route('/api/history', methods=['GET', 'POST'])
def api_history():
    if request.method == 'POST':
        data = request.json or {}
        return jsonify({'status': 'success', 'saved_session': data})
    return jsonify({'status': 'success', 'sessions': []})

if __name__ == '__main__':
    print("🚀 Starting AI Voice Assistant Web Interface on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


