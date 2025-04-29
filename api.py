from flask import Flask, request, jsonify
from patient_chatbot import PatientChatbot


app = Flask(__name__)
chatbot = PatientChatbot()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    response = chatbot.process_message(user_input)
    return jsonify({'response': response['response']})

if __name__ == "__main__":
    app.run(debug=True)