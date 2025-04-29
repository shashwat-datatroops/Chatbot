from datetime import datetime

class ConversationTracker:
    """Simple class to track conversation history"""
    def __init__(self):
        self.history = []
        self.pending_appointment = None
        self.appointment_state = None
        self.pending_verification = None
        
    def add_message(self, sender, content):
        self.history.append({
            "sender": sender,
            "content": content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    def get_history(self):
        return self.history
        
    def set_pending_appointment(self, details, state):
        self.pending_appointment = details
        self.appointment_state = state
        
    def get_pending_appointment(self):
        return self.pending_appointment, self.appointment_state
        
    def clear_pending_appointment(self):
        self.pending_appointment = None
        self.appointment_state = None

    def set_pending_verification(self, data):
        self.pending_verification = data

    def get_pending_verification(self):
        return self.pending_verification

    def clear_pending_verification(self):
        self.pending_verification = None