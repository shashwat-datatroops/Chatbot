from flask import Flask, request, jsonify
from flask_cors import CORS
from patient_chatbot import PatientChatbot

app = Flask(__name__)
CORS(app)
chatbot = PatientChatbot()
conversation_history = []

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    action = data.get('action', 'chat')

    if action == 'reset':
        conversation_history.clear()
        chatbot.reset() if hasattr(chatbot, 'reset') else None
        return jsonify({'status': 'reset', 'message': 'Conversation reset.'})

    elif action == 'get_history':
        return jsonify({'history': conversation_history})

    elif action == 'chat':
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Save user message
        conversation_history.append({
            'sender': 'user',
            'content': user_message,
            'timestamp': str(request.date)  # or use datetime.now().isoformat()
        })

        response = chatbot.process_message(user_message)
        bot_message = response['response']

        # Save bot response
        conversation_history.append({
            'sender': 'bot',
            'content': bot_message,
            'timestamp': str(request.date)
        })

        return jsonify({'response': bot_message})

    else:
        return jsonify({'error': 'Unknown action'}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5001)