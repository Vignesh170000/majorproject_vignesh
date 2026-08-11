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

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    data = request.json or {}
    provider = data.get('provider', 'Email')
    email = data.get('email', 'user@example.com')
    name = data.get('name', email.split('@')[0].capitalize())
    user_id = f"{provider.lower()}_{int(datetime.datetime.now().timestamp())}"
    return jsonify({
        'status': 'success',
        'user': {
            'id': user_id,
            'name': name,
            'email': email,
            'provider': provider
        }
    })

@app.route('/api/history', methods=['GET', 'POST'])
def api_history():
    if request.method == 'POST':
        data = request.json or {}
        return jsonify({'status': 'success', 'saved_session': data})
    return jsonify({'status': 'success', 'sessions': []})

if __name__ == '__main__':
    print("🚀 Starting AI Voice Assistant Web Interface on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
