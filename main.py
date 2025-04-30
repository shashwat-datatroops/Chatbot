from patient_chatbot import PatientChatbot

from symptomtriagesystem import integrate_symptom_triage,SymptomTriageSystem

if __name__ == "__main__":
    PatientChatbot=integrate_symptom_triage(PatientChatbot)
    chatbot = PatientChatbot()
    print("Chatbot: How can I assist you today?")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Chatbot: Goodbye!")
            break
        response = chatbot.process_message(user_input)
        print(f"Chatbot: {response['response']}")
        
        
        
        
        
        #I want to book appointment