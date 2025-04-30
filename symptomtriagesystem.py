import random
from patient_chatbot import PatientChatbot

class SymptomTriageSystem:
    """
    Handles symptom analysis, risk assessment, and recommendation generation.
    Designed to be integrated with the PatientChatbot class.
    """
    
    def __init__(self):
        
        self.symptom_department_mapping = {
            "chest pain": ["cardiology", "emergency medicine"],
            "heart palpitations": ["cardiology"],
            "rapid heartbeat": ["cardiology"],
    
            "headache": ["neurology"],
            "severe headache": ["neurology", "emergency medicine"],
            "sudden confusion": ["neurology", "emergency medicine"],
            "dizziness": ["neurology", "otolaryngology"],
            "migraine": ["neurology"],
            "fainting": ["neurology", "cardiology"],
            "seizure": ["neurology", "emergency medicine"],
    
            "abdominal pain": ["gastroenterology"],
            "severe abdominal pain": ["gastroenterology", "emergency medicine"],
            "nausea": ["gastroenterology"],
            "vomiting": ["gastroenterology"],
            "diarrhea": ["gastroenterology"],
            "constipation": ["gastroenterology"],
            "blood in stool": ["gastroenterology"],
    
            "difficulty breathing": ["pulmonology", "emergency medicine"],
            "shortness of breath": ["pulmonology", "cardiology"],
            "cough": ["pulmonology", "general physician"],
            "persistent cough": ["pulmonology"],
            "coughing up blood": ["pulmonology", "emergency medicine"],
            "wheezing": ["pulmonology", "allergy and immunology"],
    
            "joint pain": ["orthopedics", "rheumatology"],
            "back pain": ["orthopedics", "neurology"],
            "severe back pain": ["orthopedics", "neurology"],
            "muscle weakness": ["neurology", "rheumatology"],
    
            "fever": ["general physician", "infectious disease"], 
            "high fever": ["infectious disease", "general physician"], 
            "very high fever": ["infectious disease", "emergency medicine"],
            "fatigue": ["general physician", "endocrinology"],  
            "sudden weight loss": ["endocrinology", "oncology"],
            "rash": ["dermatology", "allergy and immunology"],
            "severe rash": ["dermatology", "emergency medicine"],
            "swelling": ["general physician", "rheumatology"]  
            }
        self.symptom_risk_profiles = {
            "chest pain": {"risk_level": "severe", "emergency_flag": True},
            "difficulty breathing": {"risk_level": "severe", "emergency_flag": True},
            "shortness of breath": {"risk_level": "severe", "emergency_flag": True},
            "heart palpitations": {"risk_level": "moderate", "emergency_flag": False},
            "rapid heartbeat": {"risk_level": "moderate", "emergency_flag": False},
            
            "severe headache": {"risk_level": "severe", "emergency_flag": True},
            "sudden confusion": {"risk_level": "severe", "emergency_flag": True},
            "dizziness": {"risk_level": "moderate", "emergency_flag": False},
            "headache": {"risk_level": "mild", "emergency_flag": False},
            "migraine": {"risk_level": "moderate", "emergency_flag": False},
            "fainting": {"risk_level": "moderate", "emergency_flag": False},
            "seizure": {"risk_level": "severe", "emergency_flag": True},
            
            "severe abdominal pain": {"risk_level": "severe", "emergency_flag": True},
            "abdominal pain": {"risk_level": "moderate", "emergency_flag": False},
            "nausea": {"risk_level": "mild", "emergency_flag": False},
            "vomiting": {"risk_level": "moderate", "emergency_flag": False},
            "diarrhea": {"risk_level": "mild", "emergency_flag": False},
            "constipation": {"risk_level": "mild", "emergency_flag": False},
            "blood in stool": {"risk_level": "moderate", "emergency_flag": False},
            
            "difficulty breathing": {"risk_level": "severe", "emergency_flag": True},
            "cough": {"risk_level": "mild", "emergency_flag": False},
            "persistent cough": {"risk_level": "moderate", "emergency_flag": False},
            "coughing up blood": {"risk_level": "severe", "emergency_flag": True},
            "wheezing": {"risk_level": "moderate", "emergency_flag": False},
            
            "joint pain": {"risk_level": "mild", "emergency_flag": False},
            "back pain": {"risk_level": "mild", "emergency_flag": False},
            "severe back pain": {"risk_level": "moderate", "emergency_flag": False},
            "muscle weakness": {"risk_level": "moderate", "emergency_flag": False},
            
            "fever": {"risk_level": "mild", "emergency_flag": False},
            "high fever": {"risk_level": "moderate", "emergency_flag": False},
            "very high fever": {"risk_level": "severe", "emergency_flag": True},
            "fatigue": {"risk_level": "mild", "emergency_flag": False},
            "sudden weight loss": {"risk_level": "moderate", "emergency_flag": False},
            "rash": {"risk_level": "mild", "emergency_flag": False},
            "severe rash": {"risk_level": "moderate", "emergency_flag": False},
            "swelling": {"risk_level": "mild", "emergency_flag": False},
            
            "stroke symptoms": {"risk_level": "severe", "emergency_flag": True},
            "heart attack symptoms": {"risk_level": "severe", "emergency_flag": True},
            "severe bleeding": {"risk_level": "severe", "emergency_flag": True},
            "loss of consciousness": {"risk_level": "severe", "emergency_flag": True},
            "severe allergic reaction": {"risk_level": "severe", "emergency_flag": True},
            "anaphylaxis": {"risk_level": "severe", "emergency_flag": True}
        }
        
        self.risk_modifiers = {
            "duration": {
                "few minutes": 0,
                "few hours": 0,
                "few days": 1,
                "few weeks": 1,
                "months": 2,
                "years": 1
            },
            "intensity": {
                "mild": 0,
                "moderate": 1,
                "severe": 2,
                "unbearable": 3
            },
            "frequency": {
                "rare": 0,
                "occasional": 0,
                "frequent": 1,
                "constant": 2
            },
            "age_group": {
                "infant": 2,
                "child": 1,
                "adult": 0,
                "elderly": 1
            },
            "comorbidities": {
                "diabetes": 1,
                "hypertension": 1,
                "heart disease": 2,
                "lung disease": 2,
                "immunocompromised": 2
            }
        }
        
        self.recommendation_templates = {
            "mild": {
                "message": "Your symptoms suggest a mild condition that can likely be managed with self-care.",
                "self_care": [
                    "Rest and ensure you're getting adequate sleep",
                    "Stay hydrated by drinking plenty of fluids",
                    "Take over-the-counter medications as appropriate for symptom relief",
                    "Monitor your symptoms for any changes or worsening"
                ],
                "doctor_visit": "Schedule a routine appointment with your primary care physician if symptoms persist for more than a few days or worsen.",
                "emergency": None
            },
            "moderate": {
                "message": "Your symptoms suggest a condition that may need medical attention.",
                "self_care": [
                    "Rest and avoid strenuous activities",
                    "Stay hydrated and maintain proper nutrition",
                    "Take appropriate over-the-counter medications for symptom relief if suitable"
                ],
                "doctor_visit": "We recommend scheduling an appointment with an appropriate healthcare provider within the next 1-2 days.",
                "emergency": None
            },
            "severe": {
                "message": "Your symptoms indicate a potentially serious condition that requires prompt medical attention.",
                "self_care": None,
                "doctor_visit": "Please seek medical care immediately.",
                "emergency": "If symptoms are severe or rapidly worsening, please call emergency services (911) or go to the nearest emergency room."
            }
        }
        
        self.symptom_department_mapping = {
            "chest pain": ["cardiology", "emergency medicine"],
            "heart palpitations": ["cardiology"],
            "rapid heartbeat": ["cardiology"],
            
            "headache": ["neurology"],
            "severe headache": ["neurology", "emergency medicine"],
            "sudden confusion": ["neurology", "emergency medicine"],
            "dizziness": ["neurology", "otolaryngology"],
            "migraine": ["neurology"],
            "fainting": ["neurology", "cardiology"],
            "seizure": ["neurology", "emergency medicine"],
            
            "abdominal pain": ["gastroenterology"],
            "severe abdominal pain": ["gastroenterology", "emergency medicine"],
            "nausea": ["gastroenterology"],
            "vomiting": ["gastroenterology"],
            "diarrhea": ["gastroenterology"],
            "constipation": ["gastroenterology"],
            "blood in stool": ["gastroenterology"],
            
            "difficulty breathing": ["pulmonology", "emergency medicine"],
            "shortness of breath": ["pulmonology", "cardiology"],
            "cough": ["pulmonology", "general physician"],
            "persistent cough": ["pulmonology"],
            "coughing up blood": ["pulmonology", "emergency medicine"],
            "wheezing": ["pulmonology", "allergy and immunology"],
            
            "joint pain": ["orthopedics", "rheumatology"],
            "back pain": ["orthopedics", "neurology"],
            "severe back pain": ["orthopedics", "neurology"],
            "muscle weakness": ["neurology", "rheumatology"],
            
            "fever": ["general physician", "infectious disease"],
            "high fever": ["infectious disease", "general physician"],
            "very high fever": ["infectious disease", "emergency medicine"],
            "fatigue": ["general physician", "endocrinology"],
            "sudden weight loss": ["endocrinology", "oncology"],
            "rash": ["dermatology", "allergy and immunology"],
            "severe rash": ["dermatology", "emergency medicine"],
            "swelling": ["general physician", "rheumatology"]
        }
    
    def analyze_symptoms(self, message, llm=None):
        """
        Analyze symptoms described in a message and return a comprehensive analysis.
        
        Args:
            message (str): User's message describing symptoms
            llm: Optional language model to use for more complex analysis
            
        Returns:
            dict: Analysis results including detected symptoms, risk level, and recommendations
        """
        if llm:
            return self._analyze_with_llm(message, llm)
        else:
            return self._analyze_rule_based(message)
        
    def process_appointment_selection(self, message):
        """Process doctor selection for appointment booking"""
        message_lower = message.lower().strip()
    
        if "no preference" in message_lower or message_lower in ["any", "anyone"]:
            pending = self.conversation_tracker.get_pending_appointment()
            department = pending.get("suggested_department", "General Physician").lower()
        
            valid_department = next(
                (key for key in self.doctors if key in department.lower()),
                "general physician"
            )
        
            if valid_department in self.doctors and self.doctors[valid_department]:
                selected_doctor = random.choice(self.doctors[valid_department])
                self.conversation_tracker.update_pending_appointment({
                    "department": valid_department,
                    "doctor": selected_doctor
                })
                response = f"Great! I'll book an appointment with {selected_doctor} in the {valid_department.title()} department."
            else:
                response = "No available doctors in that department. Please choose another."
                self.conversation_tracker.set_booking_state("waiting_for_department")
        
            response += " When would you like to schedule this appointment?"
            self.conversation_tracker.set_booking_state("waiting_for_date")
        
        else:
            response = "Please specify a doctor name or say 'no preference'."
    
        self.conversation_tracker.add_message("bot", response)
        return {"response": response, "intent": "appointment_booking"}
    
    
    
    def _analyze_rule_based(self, message):
        """Rule-based symptom analysis for quicker responses"""
        message = message.lower()
        
        detected_symptoms = []
        for symptom in self.symptom_risk_profiles:
            if symptom in message:
                detected_symptoms.append(symptom)
                
        if not detected_symptoms:
            return {
                "detected_symptoms": [],
                "risk_level": "unknown",
                "recommendations": {
                    "message": "I couldn't identify specific symptoms from your description. Please provide more details about what you're experiencing.",
                    "self_care": None,
                    "doctor_visit": "If you're concerned about your health, we recommend consulting with a healthcare provider.",
                    "emergency": None
                },
                "departments": ["general physician"],
                "emergency_flag": False
            }
            
        risk_levels = {"mild": 1, "moderate": 2, "severe": 3}
        max_risk = 0
        emergency_flag = False
        
        for symptom in detected_symptoms:
            profile = self.symptom_risk_profiles.get(symptom, {"risk_level": "mild", "emergency_flag": False})
            current_risk = risk_levels.get(profile["risk_level"], 1)
            max_risk = max(max_risk, current_risk)
            emergency_flag = emergency_flag or profile["emergency_flag"]
            
        risk_level = "mild"
        if max_risk == 2:
            risk_level = "moderate"
        elif max_risk == 3:
            risk_level = "severe"
            
        recommended_departments = set()
        for symptom in detected_symptoms:
            departments = self.symptom_department_mapping.get(symptom, ["general physician"])
            recommended_departments.update(departments)
            
        recommendations = self.recommendation_templates.get(risk_level, self.recommendation_templates["mild"])
        
        return {
            "detected_symptoms": detected_symptoms,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "departments": list(recommended_departments),
            "emergency_flag": emergency_flag
        }
        
    def _analyze_with_llm(self, message, llm):
        """
        Use LLM for more nuanced symptom analysis
        
        Args:
            message (str): User's message describing symptoms
            llm: Language model to use for analysis
            
        Returns:
            dict: Analysis results
        """
        from langchain.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        import json
        
        symptom_prompt = ChatPromptTemplate.from_template(
            """You are a medical symptom analyzer. Extract symptoms and risk factors from this patient's message.
            
            Patient's message: {message}
            
            Analyze the message and provide the following information in valid JSON format:
            - detected_symptoms: Array of specific symptoms mentioned
            - duration: How long the symptoms have been present (if mentioned)
            - intensity: Intensity level of symptoms (mild, moderate, severe, unbearable)
            - frequency: How often symptoms occur (rare, occasional, frequent, constant)
            - age_group: Patient's age group if mentioned (infant, child, adult, elderly)
            - comorbidities: Any existing conditions mentioned
            - risk_level: Your assessment of overall risk (mild, moderate, severe)
            - emergency_flag: Boolean indicating if immediate medical attention is needed
            
            Return ONLY valid JSON without any other text.
            """
        )
        
        try:
            symptom_chain = symptom_prompt | llm | StrOutputParser()
            result = symptom_chain.invoke({"message": message})
            
            analysis = json.loads(result)
            
            risk_level = analysis.get("risk_level", "mild")
            recommendations = self.recommendation_templates.get(risk_level, self.recommendation_templates["mild"])
            
            recommended_departments = set()
            for symptom in analysis.get("detected_symptoms", []):
                if symptom in self.symptom_department_mapping:
                    departments = self.symptom_department_mapping[symptom]
                else:
                    matched = False
                    for known_symptom, departments in self.symptom_department_mapping.items():
                        if known_symptom in symptom or symptom in known_symptom:
                            recommended_departments.update(departments)
                            matched = True
                    
                    if not matched:
                        recommended_departments.add("general physician")
            
            if not recommended_departments:
                recommended_departments.add("general physician")
                
            analysis["recommendations"] = recommendations
            analysis["departments"] = list(recommended_departments)
            
            return analysis
            
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            return self._analyze_rule_based(message)
    
    def generate_triage_response(self, analysis):
        """
        Generate a user-friendly triage response based on symptom analysis
        
        Args:
            analysis (dict): The symptom analysis results
            
        Returns:
            str: A formatted triage response
        """
        if not analysis or analysis.get("risk_level") == "unknown":
            return (
                "I need more information about your symptoms to provide helpful guidance. "
                "Could you describe what you're experiencing in more detail? "
                "For example, what symptoms are you having, when did they start, and how severe are they?"
            )
        
        risk_level = analysis.get("risk_level", "mild")
        recommendations = analysis.get("recommendations", self.recommendation_templates["mild"])
        
        response = [f"Based on the symptoms you've described ({', '.join(analysis.get('detected_symptoms', ['unspecified']))}), this appears to be a **{risk_level.upper()}** risk situation."]
        
        response.append(recommendations.get("message", ""))
        
        self_care = recommendations.get("self_care")
        if self_care:
            response.append("\n**Self-care recommendations:**")
            for tip in self_care:
                response.append(f"- {tip}")
        
        doctor_visit = recommendations.get("doctor_visit")
        if doctor_visit:
            response.append(f"\n**Medical attention:** {doctor_visit}")
        
        emergency = recommendations.get("emergency")
        if emergency:
            response.append(f"\n**IMPORTANT:** {emergency}")
        
        departments = analysis.get("departments", ["general physician"])
        if departments:
            response.append(f"\n**Recommended specialists:** {', '.join(departments)}")
        
        return "\n".join(response)


def integrate_symptom_triage(PatientChatbot):
    """
    Adds symptom triage functionality to the PatientChatbot class.
    This function should be executed after the PatientChatbot class is defined.
    """
    
    original_init = PatientChatbot.__init__
    
    def new_init(self):
        original_init(self)
        self.symptom_triage = SymptomTriageSystem()
        
        if not hasattr(self, 'doctors') or not self.doctors:
            self.doctors = {
                "general physician": ["Brown", "Wilson", "Taylor"],
                "cardiology": ["Smith", "Johnson", "Williams"],
                # Other departments...
            }
    
    PatientChatbot.__init__ = new_init
    
    def process_symptom_triage(self, message):
        """Process a message for symptom triage and generate recommendations"""
        analysis = self.symptom_triage.analyze_symptoms(message, self.report_llm)
        
        response = self.symptom_triage.generate_triage_response(analysis)
        
        if analysis.get("emergency_flag", False):
            response += (
                "\n\n**This appears to be an emergency situation.**\n"
                "Would you like me to provide the nearest emergency facilities in your area or call emergency services?"
            )
            
        if analysis.get("risk_level") in ["moderate", "severe"]:
            departments = analysis.get("departments", ["general physician"])
            primary_dept = departments[0] if departments else "general physician"
            
            response += f"\n\nWould you like me to help you book an appointment with {primary_dept}? (yes/no)"
            
            suggested_department = primary_dept.lower()
            if suggested_department.lower() in self.doctors:
                selected_doctor = random.choice(self.doctors[suggested_department])
                self.conversation_tracker.set_pending_appointment(
                    {
                        "suggested_department": suggested_department,
                        "doctor": selected_doctor
                    },
                    "waiting_for_department_confirmation"
                )
            else:
                response += "\nSorry, we don't have that department. Please choose another."
                
        return {"response": response, "analysis": analysis}
    
    PatientChatbot.process_symptom_triage = process_symptom_triage
    
    original_process_message = PatientChatbot.process_message
    
    def new_process_message(self, message):
        if not message.strip():
            return original_process_message(self, message)
            
        symptom_keywords = [
            "pain", "ache", "hurt", "fever", "cough", "headache", "rash",
            "nausea", "dizzy", "dizziness", "fatigue", "tired", "swelling", 
            "bleeding", "infection", "sick", "symptom", "not feeling well", 
            "chest", "breath", "breathing", "stomach", "vomit", "diarrhea",
            "joint", "muscle", "weakness", "numbness", "tingling"
        ]
        
        symptom_indicators = [
            "feel", "feeling", "having", "having a", "experiencing",
            "suffering", "suffered", "started", "developed", "noticed"
        ]
        
        message_lower = message.lower()
        
        has_symptoms = any(keyword in message_lower for keyword in symptom_keywords)
        has_indicators = any(indicator in message_lower for indicator in symptom_indicators)
        
        if (has_symptoms and has_indicators) or ("triage" in message_lower):
            self.conversation_tracker.add_message("user", message)
            result = self.process_symptom_triage(message)
            response = result["response"]
            self.conversation_tracker.add_message("bot", response)
            return {"response": response, "intent": "symptom_triage"}
        
        return original_process_message(self, message)
    
    PatientChatbot.process_message = new_process_message
    
    return PatientChatbot