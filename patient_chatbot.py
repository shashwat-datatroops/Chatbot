# from langchain_community.llms import Ollama
# from langchain.chains import ConversationChain
# from langchain.memory import ConversationBufferMemory
# from langchain.prompts import PromptTemplate, ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# import os
# import json
# from datetime import datetime, timedelta
# import re
# from dateparser import parse
# from dateutil.relativedelta import relativedelta
# from langchain.chains import RetrievalQA, LLMChain
# from langchain_community.vectorstores import FAISS
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# import random
# from typing import Dict, List, Optional

# from conversation_tracker import ConversationTracker
# from pdf_generator import PDFGenerator
# from config import (
#     DEPARTMENTS,
#     PROCEDURES,
#     DOCTORS,
#     AVAILABLE_TIME_SLOTS,
#     REPORTS_METADATA,
#     BOOKED_APPOINTMENTS
# )
# from utils import sanitize_response, extract_text_from_pdf

# llm = Ollama(model="mixtral")

# class PatientChatbot:
#     def __init__(self):
#         self.conversation_tracker = ConversationTracker()
#         self.pdf_generator = PDFGenerator()
        
#         self.otp_storage = {}
#         self.security_questions = {
#             "1234567890": {
#                 "question": "What is your date of birth?",
#                 "answer": "1990-01-01"
#             }
#         }
        
#         self.departments = DEPARTMENTS
#         self.procedures = PROCEDURES
#         self.doctors = DOCTORS
#         self.available_time_slots = AVAILABLE_TIME_SLOTS
#         self.reports_metadata = REPORTS_METADATA
#         self.booked_appointments = BOOKED_APPOINTMENTS
        

#     def answer_question_over_report(self, report_text, question):
#         """Answer specific questions about a medical report using direct text extraction"""
#         report_text = report_text.lower()
#         question = question.lower()
        
#         patterns = {
#             'hemoglobin': r'hemoglobin[:\s]+([\d\.]+)\s*(g/dl|g/l)',
#             'rbc': r'rbc[:\s]+([\d\.]+)\s*(million/mcl|10\^6/ul)',
#             'wbc': r'wbc[:\s]+([\d\.]+)\s*(/mcl|/ul)',
#             'platelets': r'platelets[:\s]+([\d\.]+)\s*(/mcl|/ul)',
#             'sugar': r'sugar[:\s]+([\d\.]+)\s*(mg/dl|mmol/l)',
#             'hba1c': r'hba1c[:\s]+([\d\.]+)\s*%'
#         }
        
#         for param, pattern in patterns.items():
#             if param in question:
#                 match = re.search(pattern, report_text)
#                 if match:
#                     value = match.group(1)
#                     unit = match.group(2)
#                     return f"Your {param} level was {value} {unit}."
        
#         if 'test result' in question or 'result' in question:
#             lines = report_text.split('\n')[:5]
#             return "Here are the key findings from your report:\n" + "\n".join(lines)
        
#         return "I couldn't find specific information about that in your report. Please ask about a specific parameter like hemoglobin, RBC, WBC, or platelets."

#     def process_report_query(self, message):
#         """Process medical report retrieval requests"""
#         pending_verification = self.conversation_tracker.get_pending_verification()
        
#         if pending_verification:
#             return self._verify_report_access(message, pending_verification)
            
#         if self.conversation_tracker.get_pending_verification() and self.conversation_tracker.get_pending_verification().get("state") == "waiting_for_report_selection":
#             current_report = self.conversation_tracker.get_pending_verification().get("current_report")
#             if current_report:
#                 report_text = extract_text_from_pdf(current_report["file_path"])
#                 if report_text:
#                     answer = self.answer_question_over_report(report_text, message)
#                     return {"response": answer}
            
#             for report in self.reports_metadata:
#                 report_text = extract_text_from_pdf(report["file_path"])
#                 if report_text:
#                     answer = self.answer_question_over_report(report_text, message)
#                     if answer.lower() not in ["i don't know", "i couldn't find"]:
#                         return {"response": answer}
            
#             return {"response": "I couldn't find that information in your reports."}
        
#         response = "To access your medical reports, please provide your registered phone number."
#         self.conversation_tracker.set_pending_verification({"state": "waiting_for_phone"})
#         return {"response": response}

#     def process_greeting(self, message):
#         response = "Hello! I'm your medical assistant chatbot. I can help you book appointments, answer medical questions, check insurance information, or access your medical reports. How can I assist you today?"
#         return {"response": response}
    
#     def generate_medical_response(self, question):
#         """Generate response using Mixtral model"""
#         try:
#             response = llm.invoke(
#                 f"""You are a helpful medical assistant. Provide a concise, accurate response to this question:
#                 Question: {question}
            
#                 Guidelines:
#                 - Be brief (6-8 sentences)
#                 - Use simple language for patients
#                 - If unsure, recommend consulting a doctor
#                 - Avoid speculation
#                 """
#             )
#             return response.strip()
#         except Exception as e:
#             print(f"Error using Mixtral model: {e}")
#             return (
#                 "I'm unable to provide a medical response right now. "
#                 "Please consult a healthcare professional for accurate advice."
#             )
            
#     def process_insurance_query(self, message):
#         """Process insurance-related queries"""
#         insurance_prompt = ChatPromptTemplate.from_template(
#             """You are a helpful medical insurance assistant. Based on the user's query, 
#             provide a helpful and accurate response. The user asked: {message}
            
#             Some information about our clinic's insurance policies:
#             - We accept most major insurance providers including Blue Cross, Cigna, Aetna, and United Healthcare
#             - Typical copay ranges from $20-$50 for office visits
#             - Most diagnostic tests are covered with prior authorization
#             - Specialist visits may require a referral
            
#             Please provide a concise, helpful response to the user's insurance question.
#             If they didn't specify an insurance provider, politely ask for more details.
#             Always offer to connect them with our billing department for specific questions."""
#         )
    
#         insurance_chain = insurance_prompt | llm | StrOutputParser()
    
#         response = insurance_chain.invoke({"message": message})
#         response = sanitize_response(response)
    
#         return {"response": response, "insurance_details": {"query": message}}

#     def _verify_report_access(self, message, verification_data):
#         """Verify user identity for report access"""
#         state = verification_data["state"]
#         phone_number = verification_data.get("phone_number")
        
#         if state == "waiting_for_phone":
#             phone_match = re.search(r'(\d{10}|\d{3}[-\.\s]\d{3}[-\.\s]\d{4})', message)
#             if phone_match:
#                 phone_number = re.sub(r'[^\d]', '', phone_match.group(1))
#             else:
#                 response = "I need your phone number to access your reports. Please provide your 10-digit phone number."
#                 return {"response": response}
            
#             user_reports = [r for r in self.reports_metadata if r["phone_number"] == phone_number]
#             if not user_reports:
#                 response = f"I couldn't find any reports associated with phone number {phone_number}. Please verify your phone number or contact the hospital administration."
#                 self.conversation_tracker.clear_pending_verification()
#                 return {"response": response}
            
#             self.conversation_tracker.set_pending_verification({
#                 "state": "waiting_for_verification",
#                 "phone_number": phone_number,
#                 "reports": user_reports
#             })
            
#             import random
#             otp = 123456
#             self.otp_storage[phone_number] = str(otp)
            
#             response = f"I've sent a verification code to {phone_number}. Please enter the 6-digit code to access your reports."
#             return {"response": response}
            
#         elif state == "waiting_for_verification":
#             if message == self.otp_storage.get(phone_number):
#                 reports = verification_data["reports"]
#                 response = "Verification successful! Here are your available reports:\n\n"
                
#                 for report in reports:
#                     response += f"- {report['type'].replace('_', ' ').title()} from {report['date']}\n"
                
#                 response += "\nTo view a specific report, please specify the type or date (e.g., 'Show my blood test report' or 'Show reports from June 2023')."
                
#                 self.conversation_tracker.set_pending_verification({
#                     "state": "waiting_for_report_selection",
#                     "reports": reports,
#                     "phone_number": phone_number
#                 })
                
#                 return {"response": response}
#             else:
#                 response = "Invalid verification code. Please try again or request a new code by saying 'new code'."
#                 return {"response": response}
            
#         elif state == "waiting_for_report_selection":
#             if "show" in message.lower() or "view" in message.lower():
#                 report_type = None
#                 report_date = None
                
#                 if "blood test" in message.lower():
#                     report_type = "blood_test"
#                 elif "sugar test" in message.lower():
#                     report_type = "sugar_test"
                
#                 date_match = re.search(r'(\d{4}-\d{2}|\w+ \d{4})', message)
#                 if date_match:
#                     try:
#                         parsed_date = parse(date_match.group(1))
#                         if parsed_date:
#                             report_date = parsed_date.strftime("%Y-%m")
#                     except:
#                         pass
                
#                 matching_reports = []
#                 for report in verification_data["reports"]:
#                     if report_type and report["type"] == report_type:
#                         matching_reports.append(report)
#                     elif report_date and report["date"].startswith(report_date):
#                         matching_reports.append(report)
                
#                 if matching_reports:
#                     matching_reports.sort(key=lambda x: x["date"], reverse=True)
#                     current_report = matching_reports[0]
                    
#                     verification_data["current_report"] = current_report
#                     self.conversation_tracker.set_pending_verification(verification_data)
                    
#                     response = f"Here are the matching reports:\n\n"
#                     for report in matching_reports:
#                         response += f"- {report['type'].replace('_', ' ').title()} from {report['date']}\n"
#                         response += f"  (Report available at: {report['file_path']})\n"
                    
#                     response += "\nYou can ask questions about this report?"
#                     return {"response": response}
#                 else:
#                     response = "I couldn't find any reports matching your request. Please try again with a different type or date."
#                     return {"response": response}
            
#             current_report = verification_data.get("current_report")
#             if current_report:
#                 report_text = extract_text_from_pdf(current_report["file_path"])
#                 if report_text:
#                     answer = self.answer_question_over_report(report_text, message)
#                     return {"response": answer}
            
#             for report in verification_data["reports"]:
#                 report_text = extract_text_from_pdf(report["file_path"])
#                 if report_text:
#                     answer = self.answer_question_over_report(report_text, message)
#                     if answer.lower() not in ["i don't know", "i couldn't find"]:
#                         return {"response": answer}
            
#             return {"response": "I couldn't find that information in your reports."}

#     def determine_department_from_symptoms(self, message):
#         """Determine appropriate department based on symptoms"""
#         prompt = ChatPromptTemplate.from_template(
#             """Analyze these symptoms and recommend the appropriate medical specialty:
#             Symptoms: {symptoms}
        
#             Choose from: {departments}
        
#             Return ONLY the department name from the list. 
#             If symptoms could match multiple departments, choose the most specific.
#             If uncertain, return 'General Physician'.
#             """
#         )
    
#         try:
#             departments_list = ", ".join(self.departments)
#             chain = prompt | llm | StrOutputParser()
#             department = chain.invoke({
#                 "symptoms": message,
#                 "departments": departments_list
#             }).strip().lower()
        
#             for dept in self.departments:
#                 if dept in department:
#                     return dept.title()
#             return "General Physician"
#         except Exception as e:
#             print(f"Error determining department: {e}")
#             return "General Physician"

#     def process_message(self, message):
#         """Process user message and generate response"""
#         if not message.strip():
#             _, appointment_state = self.conversation_tracker.get_pending_appointment()
#             if appointment_state:
#                 return {"response": "Please provide the requested information to continue.", "intent": "appointment_booking"}
#             return {"response": "I didn't catch that. How can I help you?", "intent": "unknown"}
        
#         self.conversation_tracker.add_message("user", message)
    
#         pending_appointment, appointment_state = self.conversation_tracker.get_pending_appointment()
#         pending_verification = self.conversation_tracker.get_pending_verification()
    
#         if pending_verification and pending_verification.get("state") == "waiting_for_report_selection":
#             report_keywords = ["hemoglobin", "rbc", "wbc", "platelets", "blood", "test", "report", "level", "count"]
#             if any(keyword in message.lower() for keyword in report_keywords):
#                 return self.process_report_query(message)
    
#         if pending_verification:
#             result = self._verify_report_access(message, pending_verification)
#             response = result["response"]
#             self.conversation_tracker.add_message("bot", response)
#             return {"response": response, "intent": "report_inquiry"}
        
#         if pending_appointment and appointment_state:
#             result = self.continue_appointment_booking(message, pending_appointment, appointment_state)
#             response = result["response"]
        
#             if result.get("appointment_completed", False):
#                 self.pdf_generator.generate_appointment_pdf(result["appointment_details"])
#                 self.conversation_tracker.clear_pending_appointment()
        
#             self.conversation_tracker.add_message("bot", response)
#             response = sanitize_response(response)
#             return {"response": response, "intent": "appointment_booking"}
        
#         symptom_keywords = ["pain", "ache", "fever", "cough", "headache", "rash", "nausea", "dizziness", "fatigue", "swelling", "bleeding", "infection", "symptom", "feeling", "experiencing"]
#         if any(keyword in message.lower() for keyword in symptom_keywords):
#             result = self.start_appointment_process(message)
#             response = result["response"]
#             self.conversation_tracker.add_message("bot", response)
#             return {"response": response, "intent": "appointment_booking"}
        
#         intent_prompt = ChatPromptTemplate.from_template(
#             """Classify this medical message:
#             Message: {message}
    
#             Categories:
#             - greeting: General greetings
#             - appointment_booking: Any request to schedule an appointment (including symptom descriptions)
#             - medical_faq: General health questions
#             - insurance_query: Insurance/billing questions
#             - report_inquiry: Requesting medical reports or specific information from reports
#             - unknown: Other messages
    
#             Return ONLY the category name."""
#         )
        
#         intent_chain = intent_prompt | llm | StrOutputParser()
    
#         try:
#             intent = intent_chain.invoke({"message": message}).strip().lower()
#             intent = re.sub(r"^.*?(greeting|appointment_booking|medical_faq|insurance_query|report_inquiry|unknown).*?$", r"\1", intent)
#             print(f"Debug - Detected intent: '{intent}'")
#         except Exception as e:
#             print(f"Error detecting intent: {e}")
#             intent = "unknown"

#         if intent == "greeting":
#             print("Debug - Processing greeting intent")
#             result = self.process_greeting(message)
#             response = result["response"]
#         elif intent == "appointment_booking":
#             result = self.start_appointment_process(message)
#             response = result["response"]
#         elif intent == "medical_faq":
#             response = self.generate_medical_response(message)
#         elif intent == "insurance_query":
#             result = self.process_insurance_query(message)
#             response = result["response"]
#         elif intent == "report_inquiry":
#             result = self.process_report_query(message)
#             response = result["response"]
#         else:
#             print(f"Debug - Unhandled intent: '{intent}', using Mixtral")
#             try:
#                 template = (
#                     "You are a helpful medical assistant chatbot. The user asked: '{message}'. "
#                     "If this is a medical question, provide a brief, accurate response. "
#                     "If it's about insurance, or reports, give a helpful response related to those topics. "
#                     "If it's an unclear or unexpected query, respond politely and redirect to medical assistance topics. "
#                     "Respond directly without any prefixes like 'Mixtral:' or annotations about the user's message."
#                 )
#                 response = llm.invoke(template.format(message=message))
            
#                 response = re.sub(r"^(Mixtral:|LLM:).*?", "", response).strip()
#             except Exception as e:
#                 print(f"Error using Mixtral: {e}")
#                 response = "I'm not sure I understand. Would you like to book an appointment, ask a medical question, check insurance information, or access your medical reports?"

#         response = sanitize_response(response)
#         self.conversation_tracker.add_message("bot", response)
#         return {"response": response, "intent": intent}
    
#     def start_appointment_process(self, message):
#         """Start the appointment booking process and collect initial information"""
#         symptom_analysis = self.analyze_symptoms(message)
        
#         if symptom_analysis["symptoms"]:
#             departments = symptom_analysis["suggested_departments"]
#             severity = symptom_analysis["severity"]
            
#             if severity == "emergency":
#                 response = "Based on your symptoms, I recommend seeking immediate medical attention. Would you like me to help you contact emergency services?"
#                 return {"response": response, "is_emergency": True}
            
#             department_list = ", ".join(departments[:-1]) + " or " + departments[-1] if len(departments) > 1 else departments[0]
#             response = f"Based on your symptoms, I recommend scheduling with {department_list}. Would you like to proceed with this department? (yes/no)"
            
#             selected_department = departments[0].lower()
#             if selected_department in self.doctors:
#                 selected_doctor = random.choice(self.doctors[selected_department])
#                 self.conversation_tracker.set_pending_appointment(
#                     {
#                         "suggested_department": departments[0],
#                         "doctor": selected_doctor
#                     },
#                     "waiting_for_department_confirmation"
#                 )
#             else:
#                 self.conversation_tracker.set_pending_appointment(
#                     {"suggested_department": departments[0]},
#                     "waiting_for_department_confirmation"
#                 )
#             return {"response": response}
        
#         try:
#             appointment_prompt = ChatPromptTemplate.from_template(
#                 """You are an AI assistant for a medical clinic that extracts appointment booking details.
#                 From the user message, extract the following fields in JSON format:
#                 - doctor: The name of the doctor requested or null if not specified
#                 - date: The appointment date requested or null if not specified
#                 - time: The appointment time requested or null if not specified
#                 - department: The medical department requested (like cardiology, dermatology) or null if not specified
#                 - procedure: The medical procedure requested (like checkup, blood test) or null if not specified
#                 - phone_number: The phone number provided or null if not specified

#                 User message: {message}

#                 Return ONLY a valid JSON object with these fields. No other text.
#                 """
#             )

#             appointment_chain = appointment_prompt | llm | StrOutputParser()
            
#             try:
#                 json_response = appointment_chain.invoke({"message": message})
#                 appointment_details = json.loads(json_response)
#             except json.JSONDecodeError:
#                 appointment_details = {
#                     "doctor": None,
#                     "department": None,
#                     "date": None,
#                     "time": None,
#                     "phone_number": None
#                 }

#             if not any(appointment_details.values()):
#                 response = "I'd be happy to book an appointment for you. Which department would you like to schedule with? (For example: cardiology, dermatology, neurology, etc.)"
#                 self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_department")
#                 return {"response": response}

#             if not appointment_details.get("department"):
#                 response = "I'd be happy to book an appointment for you. Which department would you like to schedule with? (For example: cardiology, dermatology, neurology, etc.)"
#                 self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_department")
#                 return {"response": response}

#             elif appointment_details.get("doctor") and appointment_details.get("department") and appointment_details.get("date") and not appointment_details.get("time"):
#                 response = f"Great! I'll book an appointment with Dr. {appointment_details['doctor']} in the {appointment_details['department']} department for {appointment_details['date']}. What time would you prefer? Our available slots are between 9:00 AM to 4:30 PM."
#                 self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_time")

#             elif appointment_details.get("doctor") and appointment_details.get("department") and appointment_details.get("date") and appointment_details.get("time") and not appointment_details.get("phone_number"):
#                 response = f"Perfect! I'll schedule your appointment with Dr. {appointment_details['doctor']} in the {appointment_details['department']} department for {appointment_details['date']} at {appointment_details['time']}. What phone number should we use to contact you?"
#                 self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_phone")

#             elif not appointment_details.get("doctor") and not appointment_details.get("department"):
#                 response = "I'd be happy to book an appointment for you. Which department would you like to schedule with? (For example: cardiology, dermatology, neurology, etc.)"
#                 self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_department")

#             elif not appointment_details.get("doctor"):
#                 response = f"I'll book an appointment with the {appointment_details['department']} department. Which doctor would you like to see? If you don't have a preference, I can assign a specialist from that department."
#                 self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_doctor")

#             elif not appointment_details.get("date"):
#                 response = f"Great! I'll book an appointment with Dr. {appointment_details['doctor']} in the {appointment_details['department']} department. When would you like to schedule this appointment?"
#                 self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_date")

#             else:
#                 response = self._format_appointment_confirmation(appointment_details)
#                 return {
#                     "response": sanitize_response(response),
#                     "appointment_details": appointment_details,
#                     "appointment_completed": True
#                 }

#             return {"response": sanitize_response(response)}

#         except Exception as e:
#             print(f"Error starting appointment process: {e}")
#             response = "I'm sorry, I couldn't understand your appointment request. Could you please provide details like which department you'd like to schedule with?"
#             return {"response": response}
         
#     def continue_appointment_booking(self, message, pending_appointment, state):
#         """Continue collecting information for an appointment in progress"""
        
#         if state == "waiting_for_department_confirmation":
#             confirmation = message.strip().lower()
#             if confirmation in ["yes", "y", "yeah", "ok"]:
#                 pending_appointment["department"] = pending_appointment["suggested_department"]
#                 del pending_appointment["suggested_department"]
            
#                 if pending_appointment.get('doctor'):
#                     response = f"Great! I'll book with Dr. {pending_appointment['doctor']} in {pending_appointment['department']}. When would you like to schedule?"
#                     new_state = "waiting_for_date"
#                 else:
#                     response = f"Which doctor would you like in {pending_appointment['department']}? Say 'no preference' if you don't have one."
#                     new_state = "waiting_for_doctor"
            
#                 self.conversation_tracker.set_pending_appointment(pending_appointment, new_state)
#                 return {"response": response}
        
#             response = "Please specify which department you'd like to book with: " + ", ".join(self.departments)
#             self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_department")
#             return {"response": response}
        
#         if state == "waiting_for_department":
#             department_prompt = ChatPromptTemplate.from_template(
#                 """Extract the medical department from the user's message.
#                 User message: {message}
            
#                 Valid departments include: cardiology, dermatology, neurology, orthopedics, 
#                 pediatrics, psychiatry, radiology, surgery, oncology, gynecology, urology, ent, ophthalmology
            
#                 Return ONLY the department name, or "unknown" if no department is mentioned.
#                 """
#             )
        
#             department_chain = department_prompt | llm | StrOutputParser()
            
#             try:
#                 department = department_chain.invoke({"message": message}).strip().lower()
#                 department = re.sub(r"(?i)department:\s*", "", department)
#                 department = re.sub(r"\s*\(.*?\)", "", department)
#                 department = re.sub(r"the medical department from the user's message is:\s*", "", department)
#                 department = re.sub(r"the user's message contains a valid medical department, which is\s*", "", department)
            
#                 if department == "unknown":
#                     response = "I couldn't identify a specific department. Please specify one of our departments like cardiology, dermatology, neurology, etc."
#                     response = sanitize_response(response)
#                     return {"response": response}
            
#                 pending_appointment["department"] = department
            
#                 if pending_appointment.get("doctor"):
#                     response = f"Great! I'll book an appointment with Dr. {pending_appointment.get('doctor')} in the {department} department. When would you like to schedule this appointment?"
#                     self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_date")
#                 else:
#                     response = f"Which doctor would you like to see in the {department} department? If you don't have a preference, just say 'no preference'."
#                     self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_doctor")
                
#                 response = sanitize_response(response)
#                 return {"response": response}
            
#             except Exception as e:
#                 print(f"Error processing department: {e}")
#                 response = "I'm having trouble understanding the department. Could you please specify which department you'd like to book with (e.g., cardiology, dermatology)?"
#                 response = sanitize_response(response)
#                 return {"response": response}
    
#         elif state == "waiting_for_doctor":
#             doctor_prompt = ChatPromptTemplate.from_template(
#                 """Extract ONLY the doctor's name from this message:
#                 Message: {message}

#                 Rules:
#                 - Return ONLY the full name without any prefixes like "Dr." or "Doctor"
#                 - If no name mentioned, return "no preference"
#                 - No explanations, just the name or "no preference"
#                 """
#             )
    
#             doctor_chain = doctor_prompt | llm | StrOutputParser()
    
#             try:
#                 doctor_response = doctor_chain.invoke({"message": message}).strip()
#                 doctor_response = re.sub(r"(?i)mixtral:\s*", "", doctor_response)
#                 doctor_response = re.sub(r"(?i)^(dr\.?|doctor)\s*", "", doctor_response).strip()
#                 doctor_response = re.sub(r"(?i)(dr\.?|doctor|name:|mixtral:|llm:|\")", "", doctor_response).strip()
#                 doctor_response = re.sub(r"the user's message contains a valid medical department, which is\s*", "", doctor_response)
        
#                 if doctor_response.lower() in ["no preference", "unknown", "none"]:
#                     department = pending_appointment.get('department', '').lower()
#                     department = department.replace("department", "").strip()

#                     if department in self.doctors:
#                         doctor = self.doctors[department][0]
#                         pending_appointment["doctor"] = doctor
#                         response = f"I'll assign you to {doctor} in our {department} department. When would you like to schedule this appointment?"
#                     else:
#                         pending_appointment["doctor"] = f"{department.title()} Specialist"
#                         response = f"I'll assign you to our {department.title()} Specialist. When would you like to schedule this appointment?"
#                 else:
#                     doctor_name = re.sub(r"\s*\(.*?\)", "", doctor_response).strip()
#                     pending_appointment["doctor"] = f"Dr. {doctor_name}"
            
#                     response = f"Great! I'll book an appointment with Dr. {doctor_name} in the {pending_appointment.get('department', '').title()} department. When would you like to schedule this appointment?"
        
#                 self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_date")
#                 return {"response": sanitize_response(response)}
            
#             except Exception as e:
#                 print(f"Error processing doctor: {e}")
#                 response = "I couldn't understand which doctor you'd like to see. Please provide a specific doctor's name or say 'no preference' if you don't have one."
#                 return {"response": response}
            
#         elif state == "waiting_for_date":
#             date_prompt = ChatPromptTemplate.from_template(
#                 """Extract ONLY the date from this message:
#                 Message: "{message}"
#                 Today is April 28, 2025.

#                 Rules:
#                   - Return ONLY the date in "Month Day, Year" format
#                   - No explanations or extra text
#                   - If unclear, return "unknown"

#                 Examples:
#                 User: "Next Tuesday" -> "April 29, 2025"
#                 User: "May 5th" -> "May 5, 2025"
#                 """
#             )
    
#             date_chain = date_prompt | llm | StrOutputParser()
    
#             try:
#                 date_response = date_chain.invoke({"message": message}).strip()
#                 date_match = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", date_response)
#                 if date_match:
#                     date = date_match.group(1)
#                 elif date_response.lower() == "unknown":
#                     today = datetime.now()
#                     next_day = today + timedelta(days=1)
#                     while next_day.weekday() >= 5:
#                         next_day += timedelta(days=1)
#                     date = next_day.strftime("%B %d, %Y")
#                     response = f"I'll schedule your appointment for our next available slot on {date}. What time would you prefer? Our available slots are between 9:00 AM to 4:30 PM."
#                 else:
#                     date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}", date_response)
#                     date = date_match.group(0) if date_match else datetime.now().strftime("%B %d, %Y")
                
#                 doctor_info = pending_appointment.get('doctor', '')
#                 if doctor_info:
#                     doctor_info = re.sub(r"(?i)mixtral:\s*", "", doctor_info)
#                     doctor_info = re.sub(r"(?i)dr\.?\s*", "", doctor_info).strip()
#                     doctor_info = f"Dr. {doctor_info}"
#                     pending_appointment['doctor'] = doctor_info
                
#                 response = f"Perfect! I'll schedule your {pending_appointment.get('department', '').title()} appointment with {doctor_info} for {date}. What time would you prefer? Our available slots are between 9:00 AM to 4:30 PM."
        
#                 pending_appointment["date"] = date
#                 self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_time")
#                 return {"response": sanitize_response(response)}
        
#             except Exception as e:
#                 print(f"Error processing date: {e}")
#                 response = "I couldn't understand the date. Could you please provide a specific date for your appointment? For example, 'April 25, 2025'."
#                 return {"response": response}
            
#         elif state == "waiting_for_time":
#             time_prompt = ChatPromptTemplate.from_template(
#                     """Extract the time from this message and format it as a standard 12-hour time:
#                     Message: {message}

#                     Return the time in format "HH:MM AM/PM" (e.g., "10:00 AM").
#                     If no clear time is provided, return "unknown".
#                 """
#                 )

#             time_chain = time_prompt | llm | StrOutputParser()

#             try:
#                 requested_time = time_chain.invoke({"message": message}).strip()
#                 requested_time = re.sub(r'"', '', requested_time)
                
#                 time_match = re.search(r'(\d{1,2}:\d{2} [AP]M)', requested_time, re.IGNORECASE)
#                 if not time_match:
#                     raise ValueError("Invalid time format")
                
#                 formatted_time = time_match.group(1).upper()
#                 pending_date = pending_appointment.get("date", "")
                
#                 if pending_date in self.booked_appointments:
#                     if formatted_time in self.booked_appointments[pending_date]:
#                         alternatives = [t for t in self.available_time_slots 
#                                       if t not in self.booked_appointments[pending_date]]
#                         response = (f"Sorry, {formatted_time} is already booked. "
#                                   f"Available times on {pending_date}: {', '.join(alternatives)}")
#                         return {"response": response}
#                     else:
#                         self.booked_appointments[pending_date].append(formatted_time)
#                 else:
#                     self.booked_appointments[pending_date] = [formatted_time]
                
#                 pending_appointment["time"] = formatted_time
#                 response = "Great! What phone number should we use to confirm your appointment?"
#                 self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_phone")
#                 return {"response": sanitize_response(response)}

#             except Exception as e:
#                 print(f"Error processing time: {e}")
#                 response = ("I couldn't understand the time. Please choose from our available slots: " 
#                           + ", ".join(self.available_time_slots))
#                 return {"response": response}

#         elif state == "waiting_for_phone":
#             phone_match = re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', message)
#             if phone_match:
#                 phone_number = phone_match.group(1)
#                 pending_appointment["phone_number"] = phone_number
                
#                 confirmation = self._format_appointment_confirmation(pending_appointment)
#                 self.conversation_tracker.clear_pending_appointment()
#                 return {
#                     "response": sanitize_response(confirmation),
#                     "appointment_details": pending_appointment,
#                     "appointment_completed": True
#                 }
#             else:
#                 response = "I didn't catch a valid phone number. Please provide your phone number in any format (e.g. 123-456-7890)."
#                 return {"response": response}

#         else:
#             response = "I'm having trouble processing your appointment. Let's start over."
#             self.conversation_tracker.clear_pending_appointment()
#             return {"response": response}

#     def _format_appointment_confirmation(self, details):
#         """Format final appointment confirmation message"""
#         return (
#             f"Appointment confirmed!\n"
#             f"Doctor: {details.get('doctor', 'Not specified')}\n"
#             f"Department: {details.get('department', 'Not specified')}\n"
#             f"Date: {details.get('date', 'Not specified')}\n"
#             f"Time: {details.get('time', 'Not specified')}\n"
#             f"Phone: {details.get('phone_number', 'Not provided')}\n\n"
#             f"A confirmation PDF has been generated. Please arrive 15 minutes early!"
#         )

#     def analyze_symptoms(self, message):
#         """Analyze symptoms in the message and return analysis results"""
#         message = message.lower()
#         symptoms = []
#         severity = "moderate"
        
#         symptom_patterns = {
#             "headache": ["neurology", "general physician"],
#             "migraine": ["neurology"],
#             "fever": ["general physician"],
#             "cough": ["pulmonology", "general physician"],
#             "chest pain": ["cardiology", "emergency"],
#             "abdominal pain": ["gastroenterology", "general physician"],
#             "rash": ["dermatology"],
#             "joint pain": ["orthopedics", "rheumatology"],
#             "back pain": ["orthopedics", "physical medicine"],
#             "anxiety": ["psychiatry", "general physician"],
#             "depression": ["psychiatry"],
#             "dizziness": ["neurology", "cardiology"],
#             "nausea": ["gastroenterology", "general physician"],
#             "vomiting": ["gastroenterology", "general physician"],
#             "fatigue": ["general physician", "endocrinology"],
#             "shortness of breath": ["pulmonology", "cardiology", "emergency"],
#             "swelling": ["general physician", "nephrology"],
#             "bleeding": ["hematology", "emergency"],
#             "infection": ["infectious disease", "general physician"],
#             "allergy": ["allergy", "immunology"],
#             "vision problems": ["ophthalmology"],
#             "hearing problems": ["ent"],
#             "urinary problems": ["urology"],
#             "menstrual problems": ["gynecology"]
#         }
        
#         severity_indicators = {
#             "emergency": ["severe", "intense", "unbearable", "emergency", "urgent", "critical", "life-threatening"],
#             "high": ["high", "strong", "significant", "persistent", "chronic", "frequent"],
#             "moderate": ["moderate", "mild", "occasional", "intermittent"]
#         }
        
#         for symptom, departments in symptom_patterns.items():
#             if symptom in message:
#                 symptoms.append(symptom)
        
#         for level, indicators in severity_indicators.items():
#             if any(indicator in message for indicator in indicators):
#                 severity = level
#                 break
        
#         suggested_departments = set()
#         for symptom in symptoms:
#             if symptom in symptom_patterns:
#                 suggested_departments.update(symptom_patterns[symptom])
        
#         if not symptoms and any(keyword in message for keyword in ["pain", "ache", "symptom", "feeling", "experiencing"]):
#             suggested_departments.add("general physician")
        
#         if not suggested_departments:
#             suggested_departments.add("general physician")
        
#         return {
#             "symptoms": symptoms,
#             "suggested_departments": list(suggested_departments),
#             "severity": severity
#         }






























from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import json
from datetime import datetime, timedelta
import re
from dateparser import parse
from dateutil.relativedelta import relativedelta
from langchain.chains import RetrievalQA, LLMChain
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import random
from typing import Dict, List, Optional

from conversation_tracker import ConversationTracker
from pdf_generator import PDFGenerator
from config import (
    DEPARTMENTS,
    PROCEDURES,
    DOCTORS,
    AVAILABLE_TIME_SLOTS,
    REPORTS_METADATA,
    BOOKED_APPOINTMENTS
)
from utils import sanitize_response, extract_text_from_pdf

llm = Ollama(model="mixtral")

class PatientChatbot:
    def __init__(self):
        self.conversation_tracker = ConversationTracker()
        self.pdf_generator = PDFGenerator()
        
        self.otp_storage = {}
        self.security_questions = {
            "1234567890": {
                "question": "What is your date of birth?",
                "answer": "1990-01-01"
            }
        }
        
        self.departments = DEPARTMENTS
        self.procedures = PROCEDURES
        self.doctors = DOCTORS
        self.available_time_slots = AVAILABLE_TIME_SLOTS
        self.reports_metadata = REPORTS_METADATA
        self.booked_appointments = BOOKED_APPOINTMENTS
        
        self.report_llm = Ollama(model="mixtral")
        self.qa_chain = self._create_qa_chain()
        
    def _create_qa_chain(self):
        """Create the LLM chain for medical report analysis"""
        prompt = PromptTemplate(
            input_variables=["report", "question"],
            template="""Analyze this medical report and answer the patient's question.
            
            Medical Report Excerpt:
            {report}
            
            Patient Question: 
            {question}
            
            Guidelines:
            1. Be factual and concise
            2. Highlight abnormal values
            3. Never provide medical advice
            4. Format numbers clearly
            5. If unsure, request clarification
            
            Answer:"""
        )
        return prompt | self.report_llm | StrOutputParser()
    
    def answer_question_over_report(self, report_text, question):
        """Enhanced hybrid question answering"""
        rule_answer = self._rule_based_extraction(report_text, question)
        if rule_answer:
            return rule_answer
            
        return self._llm_report_analysis(report_text, question)
    
    def _rule_based_extraction(self, report_text, question):
        """Existing regex-based logic"""
        report_text = report_text.lower()
        question = question.lower()
        
        patterns = {
            'hemoglobin': r'hemoglobin[:\s]+([\d\.]+)\s*(g/dl|g/l)',
            'rbc': r'rbc[:\s]+([\d\.]+)\s*(million/mcl|10\^6/ul)',
            'wbc': r'wbc[:\s]+([\d\.]+)\s*(/mcl|/ul)',
            'platelets': r'platelets[:\s]+([\d\.]+)\s*(/mcl|/ul)',
            'sugar': r'sugar[:\s]+([\d\.]+)\s*(mg/dl|mmol/l)',
            'hba1c': r'hba1c[:\s]+([\d\.]+)\s*%'
        }
        
        for param, pattern in patterns.items():
            if param in question:
                match = re.search(pattern, report_text)
                if match:
                    return f"Your {param} level was {match.group(1)} {match.group(2)}."
        
        if 'test result' in question or 'result' in question:
            lines = report_text.split('\n')[:5]
            return "Here are the key findings from your report:\n" + "\n".join(lines)
        
        return None
    
    def _llm_report_analysis(self, report_text, question):
        """Handle complex questions with LLM"""
        try:
            truncated = self._truncate_report(report_text, 3000)
            
            response = self.qa_chain.invoke({
                "report": truncated,
                "question": question
            })
            return self._sanitize_response(response)
        except Exception as e:
            print(f"LLM Analysis Error: {e}")
            return "I need to consult a specialist for that question. Please contact your doctor."
        
    def _truncate_report(self, text, max_length):
        """Ensure report fits LLM context window"""
        return text[:max_length] + '...' if len(text) > max_length else text

    def _sanitize_response(self, response):
        """Safety checks for LLM output"""
        response = re.sub(r"(?i)consult your doctor immediately", "", response)
        response = re.sub(r"\b(?:diagnos|treat|prescrib)\w+", "[medical advice removed]", response)
        return response.strip()

    def process_report_query(self, message):
        """Process medical report retrieval requests"""
        pending_verification = self.conversation_tracker.get_pending_verification()
        
        if pending_verification:
            return self._verify_report_access(message, pending_verification)
            
        response = "To access your medical reports, please provide your registered phone number."
        self.conversation_tracker.set_pending_verification({"state": "waiting_for_phone"})
        return {"response": response}

    def process_greeting(self, message):
        response = "Hello! I'm your medical assistant chatbot. I can help you book appointments, answer medical questions, check insurance information, or access your medical reports. How can I assist you today?"
        return {"response": response}
    
    def generate_medical_response(self, question):
        """Generate response using Mixtral model"""
        try:
            response = llm.invoke(
                f"""You are a helpful medical assistant. Provide a concise, accurate response to this question:
                Question: {question}
            
                Guidelines:
                - Be brief (6-8 sentences)
                - Use simple language for patients
                - If unsure, recommend consulting a doctor
                - Avoid speculation
                """
            )
            return response.strip()
        except Exception as e:
            print(f"Error using Mixtral model: {e}")
            return (
                "I'm unable to provide a medical response right now. "
                "Please consult a healthcare professional for accurate advice."
            )
            
    def process_insurance_query(self, message):
        """Process insurance-related queries"""
        insurance_prompt = ChatPromptTemplate.from_template(
            """You are a helpful medical insurance assistant. Based on the user's query, 
            provide a helpful and accurate response. The user asked: {message}
            
            Some information about our clinic's insurance policies:
            - We accept most major insurance providers including Blue Cross, Cigna, Aetna, and United Healthcare
            - Typical copay ranges from $20-$50 for office visits
            - Most diagnostic tests are covered with prior authorization
            - Specialist visits may require a referral
            
            Please provide a concise, helpful response to the user's insurance question.
            If they didn't specify an insurance provider, politely ask for more details.
            Always offer to connect them with our billing department for specific questions."""
        )
    
        insurance_chain = insurance_prompt | llm | StrOutputParser()
    
        response = insurance_chain.invoke({"message": message})
        response = sanitize_response(response)
    
        return {"response": response, "insurance_details": {"query": message}}

    def _verify_report_access(self, message, verification_data):
        """Verify user identity for report access"""
        state = verification_data["state"]
        phone_number = verification_data.get("phone_number")
        
        if state == "waiting_for_phone":
            phone_match = re.search(r'(\d{10}|\d{3}[-\.\s]\d{3}[-\.\s]\d{4})', message)
            if phone_match:
                phone_number = re.sub(r'[^\d]', '', phone_match.group(1))
            else:
                response = "I need your phone number to access your reports. Please provide your 10-digit phone number."
                return {"response": response}
            
            user_reports = [r for r in self.reports_metadata if r["phone_number"] == phone_number]
            if not user_reports:
                response = f"I couldn't find any reports associated with phone number {phone_number}. Please verify your phone number or contact the hospital administration."
                self.conversation_tracker.clear_pending_verification()
                return {"response": response}
            
            self.conversation_tracker.set_pending_verification({
                "state": "waiting_for_verification",
                "phone_number": phone_number,
                "reports": user_reports
            })
            
            otp = "123456"
            self.otp_storage[phone_number] = otp
            
            response = f"I've sent a verification code to {phone_number}. Please enter the 6-digit code to access your reports."
            return {"response": response}
            
        elif state == "waiting_for_verification":
            if message.strip() == self.otp_storage.get(phone_number, ''):
                reports = verification_data["reports"]
                response = "Verification successful! Here are your available reports:\n\n"
                
                for report in reports:
                    response += f"- {report['type'].replace('_', ' ').title()} from {report['date']}\n"
                
                response += "\nTo view a specific report, please specify the type or date (e.g., 'Show my blood test report' or 'Show reports from June 2023')."
                
                self.conversation_tracker.set_pending_verification({
                    "state": "waiting_for_report_selection",
                    "reports": reports,
                    "phone_number": phone_number
                })
                
                return {"response": response}
            else:
                response = "Invalid verification code. Please try again or request a new code by saying 'new code'."
                return {"response": response}
            
        elif state == "waiting_for_report_selection":
            if "show" in message.lower() or "view" in message.lower():
                report_type = None
                report_date = None
                
                if "blood test" in message.lower():
                    report_type = "blood_test"
                elif "sugar test" in message.lower():
                    report_type = "sugar_test"
                
                date_match = re.search(r'(\d{4}-\d{2}|\w+ \d{4})', message)
                if date_match:
                    try:
                        parsed_date = parse(date_match.group(1))
                        if parsed_date:
                            report_date = parsed_date.strftime("%Y-%m")
                    except Exception as e:
                        print(f"Date parsing error: {e}")
                
                matching_reports = []
                for report in verification_data["reports"]:
                    if report_type and report["type"] == report_type:
                        matching_reports.append(report)
                    elif report_date and report["date"].startswith(report_date):
                        matching_reports.append(report)
                
                if matching_reports:
                    matching_reports.sort(key=lambda x: x["date"], reverse=True)
                    current_report = matching_reports[0]
                    
                    verification_data["current_report"] = current_report
                    self.conversation_tracker.set_pending_verification(verification_data)
                    
                    response = "Here are the matching reports:\n\n"
                    for report in matching_reports:
                        response += f"- {report['type'].replace('_', ' ').title()} from {report['date']}\n"
                        response += f"  (Report available at: {report['file_path']})\n"
                    
                    response += "\nYou can ask questions about this report."
                    return {"response": response}
                else:
                    response = "I couldn't find any reports matching your request. Please try again with a different type or date."
                    return {"response": response}
            
            current_report = verification_data.get("current_report")
            if current_report:
                report_text = extract_text_from_pdf(current_report["file_path"])
                if report_text:
                    answer = self.answer_question_over_report(report_text, message)
                    return {"response": answer}
            
            for report in verification_data["reports"]:
                report_text = extract_text_from_pdf(report["file_path"])
                if report_text:
                    answer = self.answer_question_over_report(report_text, message)
                    if answer.lower() not in ["i don't know", "i couldn't find"]:
                        return {"response": answer}
            
            return {"response": "I couldn't find that information in your reports."}

    def determine_department_from_symptoms(self, message):
        """Determine appropriate department based on symptoms"""
        prompt = ChatPromptTemplate.from_template(
            """Analyze these symptoms and recommend the appropriate medical specialty:
            Symptoms: {symptoms}
        
            Choose from: {departments}
        
            Return ONLY the department name from the list. 
            If symptoms could match multiple departments, choose the most specific.
            If uncertain, return 'General Physician'.
            """
        )
    
        try:
            departments_list = ", ".join(self.departments)
            chain = prompt | llm | StrOutputParser()
            department = chain.invoke({
                "symptoms": message,
                "departments": departments_list
            }).strip().lower()
        
            for dept in self.departments:
                if dept.lower() in department.lower():
                    return dept.title()
            return "General Physician"
        except Exception as e:
            print(f"Error determining department: {e}")
            return "General Physician"

    def process_message(self, message):
        """Process user message and generate response"""
        if not message.strip():
            _, appointment_state = self.conversation_tracker.get_pending_appointment()
            if appointment_state:
                return {"response": "Please provide the requested information to continue.", "intent": "appointment_booking"}
            return {"response": "I didn't catch that. How can I help you?", "intent": "unknown"}
        
        self.conversation_tracker.add_message("user", message)
    
        pending_appointment, appointment_state = self.conversation_tracker.get_pending_appointment()
        pending_verification = self.conversation_tracker.get_pending_verification()
    
        if pending_verification and pending_verification.get("state") == "waiting_for_report_selection":
            report_keywords = ["hemoglobin", "rbc", "wbc", "platelets", "blood", "test", "report", "level", "count"]
            if any(keyword in message.lower() for keyword in report_keywords):
                return self.process_report_query(message)
    
        if pending_verification:
            result = self._verify_report_access(message, pending_verification)
            response = result["response"]
            self.conversation_tracker.add_message("bot", response)
            return {"response": response, "intent": "report_inquiry"}
        
        if pending_appointment and appointment_state:
            result = self.continue_appointment_booking(message, pending_appointment, appointment_state)
            response = result["response"]
        
            if result.get("appointment_completed", False):
                self.pdf_generator.generate_appointment_pdf(result["appointment_details"])
                self.conversation_tracker.clear_pending_appointment()
        
            self.conversation_tracker.add_message("bot", response)
            response = sanitize_response(response)
            return {"response": response, "intent": "appointment_booking"}
        
        symptom_keywords = ["pain", "ache", "fever", "cough", "headache", "rash", "nausea", "dizziness", "fatigue", "swelling", "bleeding", "infection", "symptom", "feeling", "experiencing"]
        if any(keyword in message.lower() for keyword in symptom_keywords):
            result = self.start_appointment_process(message)
            response = result["response"]
            self.conversation_tracker.add_message("bot", response)
            return {"response": response, "intent": "appointment_booking"}
        
        intent_prompt = ChatPromptTemplate.from_template(
            """Classify this medical message:
            Message: {message}
    
            Categories:
            - greeting: General greetings
            - appointment_booking: Any request to schedule an appointment (including symptom descriptions)
            - medical_faq: General health questions
            - insurance_query: Insurance/billing questions
            - report_inquiry: Requesting medical reports or specific information from reports
            - unknown: Other messages
    
            Return ONLY the category name."""
        )
        
        intent_chain = intent_prompt | llm | StrOutputParser()
    
        try:
            intent = intent_chain.invoke({"message": message}).strip().lower()
            intent = re.sub(r"^.*?(greeting|appointment_booking|medical_faq|insurance_query|report_inquiry|unknown).*?$", r"\1", intent)
            print(f"Debug - Detected intent: '{intent}'")
        except Exception as e:
            print(f"Error detecting intent: {e}")
            intent = "unknown"

        if intent == "greeting":
            print("Debug - Processing greeting intent")
            result = self.process_greeting(message)
            response = result["response"]
        elif intent == "appointment_booking":
            result = self.start_appointment_process(message)
            response = result["response"]
        elif intent == "medical_faq":
            response = self.generate_medical_response(message)
        elif intent == "insurance_query":
            result = self.process_insurance_query(message)
            response = result["response"]
        elif intent == "report_inquiry":
            result = self.process_report_query(message)
            response = result["response"]
        else:
            print(f"Debug - Unhandled intent: '{intent}', using Mixtral")
            try:
                template = (
                    "You are a helpful medical assistant chatbot. The user asked: '{message}'. "
                    "If this is a medical question, provide a brief, accurate response. "
                    "If it's about insurance, or reports, give a helpful response related to those topics. "
                    "If it's an unclear or unexpected query, respond politely and redirect to medical assistance topics. "
                    "Respond directly without any prefixes like 'Mixtral:' or annotations about the user's message."
                )
                response = llm.invoke(template.format(message=message))
            
                response = re.sub(r"^(Mixtral:|LLM:).*?", "", response).strip()
            except Exception as e:
                print(f"Error using Mixtral: {e}")
                response = "I'm not sure I understand. Would you like to book an appointment, ask a medical question, check insurance information, or access your medical reports?"

        response = sanitize_response(response)
        self.conversation_tracker.add_message("bot", response)
        return {"response": response, "intent": intent}
    
    def start_appointment_process(self, message):
        """Start the appointment booking process and collect initial information"""
        symptom_analysis = self.analyze_symptoms(message)
        
        if symptom_analysis["symptoms"]:
            departments = symptom_analysis["suggested_departments"]
            severity = symptom_analysis["severity"]
            
            if severity == "emergency":
                response = "Based on your symptoms, I recommend seeking immediate medical attention. Would you like me to help you contact emergency services?"
                return {"response": response, "is_emergency": True}
            
            department_list = ", ".join(departments[:-1]) + " or " + departments[-1] if len(departments) > 1 else departments[0]
            response = f"Based on your symptoms, I recommend scheduling with {department_list}. Would you like to proceed with this department? (yes/no)"
            
            selected_department = departments[0].lower()
            if selected_department in self.doctors:
                selected_doctor = random.choice(self.doctors[selected_department])
                self.conversation_tracker.set_pending_appointment(
                    {
                        "suggested_department": departments[0],
                        "doctor": selected_doctor
                    },
                    "waiting_for_department_confirmation"
                )
            else:
                self.conversation_tracker.set_pending_appointment(
                    {"suggested_department": departments[0]},
                    "waiting_for_department_confirmation"
                )
            return {"response": response}
        
        try:
            appointment_prompt = ChatPromptTemplate.from_template(
                """You are an AI assistant for a medical clinic that extracts appointment booking details.
                From the user message, extract the following fields in JSON format:
                - doctor: The name of the doctor requested or null if not specified
                - date: The appointment date requested or null if not specified
                - time: The appointment time requested or null if not specified
                - department: The medical department requested (like cardiology, dermatology) or null if not specified
                - procedure: The medical procedure requested (like checkup, blood test) or null if not specified
                - phone_number: The phone number provided or null if not specified

                User message: {message}

                Return ONLY a valid JSON object with these fields. No other text.
                """
            )

            appointment_chain = appointment_prompt | llm | StrOutputParser()
            
            try:
                json_response = appointment_chain.invoke({"message": message})
                appointment_details = json.loads(json_response)
            except json.JSONDecodeError:
                appointment_details = {
                    "doctor": None,
                    "department": None,
                    "date": None,
                    "time": None,
                    "phone_number": None
                }

            if not any(appointment_details.values()):
                response = "I'd be happy to book an appointment for you. Which department would you like to schedule with? (For example: cardiology, dermatology, neurology, etc.)"
                self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_department")
                return {"response": response}

            if not appointment_details.get("department"):
                response = "I'd be happy to book an appointment for you. Which department would you like to schedule with? (For example: cardiology, dermatology, neurology, etc.)"
                self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_department")
                return {"response": response}

            elif appointment_details.get("doctor") and appointment_details.get("department") and appointment_details.get("date") and not appointment_details.get("time"):
                response = f"Great! I'll book an appointment with Dr. {appointment_details['doctor']} in the {appointment_details['department']} department for {appointment_details['date']}. What time would you prefer? Our available slots are between 9:00 AM to 4:30 PM."
                self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_time")
                return {"response": response}

            elif appointment_details.get("doctor") and appointment_details.get("department") and appointment_details.get("date") and appointment_details.get("time") and not appointment_details.get("phone_number"):
                response = f"Perfect! I'll schedule your appointment with Dr. {appointment_details['doctor']} in the {appointment_details['department']} department for {appointment_details['date']} at {appointment_details['time']}. What phone number should we use to contact you?"
                self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_phone")
                return {"response": response}

            elif not appointment_details.get("doctor") and not appointment_details.get("department"):
                response = "I'd be happy to book an appointment for you. Which department would you like to schedule with? (For example: cardiology, dermatology, neurology, etc.)"
                self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_department")
                return {"response": response}

            elif not appointment_details.get("doctor"):
                response = f"I'll book an appointment with the {appointment_details['department']} department. Which doctor would you like to see? If you don't have a preference, I can assign a specialist from that department."
                self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_doctor")
                return {"response": response}

            elif not appointment_details.get("date"):
                response = f"Great! I'll book an appointment with Dr. {appointment_details['doctor']} in the {appointment_details['department']} department. When would you like to schedule this appointment?"
                self.conversation_tracker.set_pending_appointment(appointment_details, "waiting_for_date")
                return {"response": response}

            else:
                response = self._format_appointment_confirmation(appointment_details)
                return {
                    "response": sanitize_response(response),
                    "appointment_details": appointment_details,
                    "appointment_completed": True
                }

        except Exception as e:
            print(f"Error starting appointment process: {e}")
            response = "I'm sorry, I couldn't understand your appointment request. Could you please provide details like which department you'd like to schedule with?"
            return {"response": response}
         
    def continue_appointment_booking(self, message, pending_appointment, state):
        """Continue collecting information for an appointment in progress"""
        
        if state == "waiting_for_department_confirmation":
            confirmation = message.strip().lower()
            if confirmation in ["yes", "y", "yeah", "ok"]:
                pending_appointment["department"] = pending_appointment["suggested_department"]
                del pending_appointment["suggested_department"]
            
                if pending_appointment.get('doctor'):
                    response = f"Great! I'll book with Dr. {pending_appointment['doctor']} in {pending_appointment['department']}. When would you like to schedule?"
                    new_state = "waiting_for_date"
                else:
                    response = f"Which doctor would you like in {pending_appointment['department']}? Say 'no preference' if you don't have one."
                    new_state = "waiting_for_doctor"
            
                self.conversation_tracker.set_pending_appointment(pending_appointment, new_state)
                return {"response": response}
        
            response = "Please specify which department you'd like to book with: " + ", ".join(self.departments)
            self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_department")
            return {"response": response}
        
        if state == "waiting_for_department":
            department_prompt = ChatPromptTemplate.from_template(
                """Extract the medical department from the user's message.
                User message: {message}
            
                Valid departments include: cardiology, dermatology, neurology, orthopedics, 
                pediatrics, psychiatry, radiology, surgery, oncology, gynecology, urology, ent, ophthalmology
            
                Return ONLY the department name, or "unknown" if no department is mentioned.
                """
            )
        
            department_chain = department_prompt | llm | StrOutputParser()
            
            try:
                department = department_chain.invoke({"message": message}).strip().lower()
                department = re.sub(r"(?i)department:\s*", "", department)
                department = re.sub(r"\s*\(.*?\)", "", department)
                department = re.sub(r"the medical department from the user's message is:\s*", "", department)
                department = re.sub(r"the user's message contains a valid medical department, which is\s*", "", department)
            
                if department == "unknown":
                    response = "I couldn't identify a specific department. Please specify one of our departments like cardiology, dermatology, neurology, etc."
                    response = sanitize_response(response)
                    return {"response": response}
            
                pending_appointment["department"] = department
            
                if pending_appointment.get("doctor"):
                    response = f"Great! I'll book an appointment with Dr. {pending_appointment.get('doctor')} in the {department} department. When would you like to schedule this appointment?"
                    self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_date")
                else:
                    response = f"Which doctor would you like to see in the {department} department? If you don't have a preference, just say 'no preference'."
                    self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_doctor")
                
                response = sanitize_response(response)
                return {"response": response}
            
            except Exception as e:
                print(f"Error processing department: {e}")
                response = "I'm having trouble understanding the department. Could you please specify which department you'd like to book with (e.g., cardiology, dermatology)?"
                response = sanitize_response(response)
                return {"response": response}
    
        elif state == "waiting_for_doctor":
            doctor_prompt = ChatPromptTemplate.from_template(
                """Extract ONLY the doctor's name from this message:
                Message: {message}

                Rules:
                - Return ONLY the full name without any prefixes like "Dr." or "Doctor"
                - If no name mentioned, return "no preference"
                - No explanations, just the name or "no preference"
                """
            )
    
            doctor_chain = doctor_prompt | llm | StrOutputParser()
    
            try:
                doctor_response = doctor_chain.invoke({"message": message}).strip()
                doctor_response = re.sub(r"(?i)mixtral:\s*", "", doctor_response)
                doctor_response = re.sub(r"(?i)^(dr\.?|doctor)\s*", "", doctor_response).strip()
                doctor_response = re.sub(r"(?i)(dr\.?|doctor|name:|mixtral:|llm:|\")", "", doctor_response).strip()
                doctor_response = re.sub(r"the user's message contains a valid medical department, which is\s*", "", doctor_response)
        
                if doctor_response.lower() in ["no preference", "unknown", "none"]:
                    department = pending_appointment.get('department', '').lower()
                    department = department.replace("department", "").strip()

                    if department in self.doctors:
                        doctor = self.doctors[department][0]
                        pending_appointment["doctor"] = doctor
                        response = f"I'll assign you to {doctor} in our {department} department. When would you like to schedule this appointment?"
                    else:
                        pending_appointment["doctor"] = f"{department.title()} Specialist"
                        response = f"I'll assign you to our {department.title()} Specialist. When would you like to schedule this appointment?"
                else:
                    doctor_name = re.sub(r"\s*\(.*?\)", "", doctor_response).strip()
                    pending_appointment["doctor"] = f"Dr. {doctor_name}"
            
                    response = f"Great! I'll book an appointment with Dr. {doctor_name} in the {pending_appointment.get('department', '').title()} department. When would you like to schedule this appointment?"
        
                self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_date")
                return {"response": sanitize_response(response)}
            
            except Exception as e:
                print(f"Error processing doctor: {e}")
                response = "I couldn't understand which doctor you'd like to see. Please provide a specific doctor's name or say 'no preference' if you don't have one."
                return {"response": response}
            
        elif state == "waiting_for_date":   
            date_prompt = ChatPromptTemplate.from_template(
                """Extract ONLY the date from this message:
                Message: "{message}"
                Today is April 29, 2025.

                Rules:
                - Return ONLY the date in "Month Day, Year" format
                - No explanations or extra text
                - If unclear, return "unknown"

                Examples:
                User: "May 5th" -> "May 5, 2025"
                User: "June 1" -> "June 1, 2025"
                """
            )

            date_chain = date_prompt | llm | StrOutputParser()

            try:
                date_response = date_chain.invoke({"message": message}).strip()
                date_match = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", date_response)
                if date_match:
                    date = date_match.group(1)
                elif date_response.lower() == "unknown":
                    today = datetime.now()
                    next_day = today + timedelta(days=1)
                    while next_day.weekday() >= 5:
                        next_day += timedelta(days=1)
                    date = next_day.strftime("%B %d, %Y")
                    response = f"I'll schedule your appointment for our next available slot on {date}. What time would you prefer? Our available slots are between 9:00 AM to 4:30 PM."
                else:
                    date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}", date_response)
                    date = date_match.group(0) if date_match else datetime.now().strftime("%B %d, %Y")
            except Exception as e:
                print(f"Error processing date: {e}")
                today = datetime.now()
                next_day = today + timedelta(days=1)
                date = next_day.strftime("%B %d, %Y")
    
            doctor_info = pending_appointment.get('doctor', '')
            if doctor_info:
                doctor_info = re.sub(r"(?i)mixtral:\s*", "", doctor_info)
                doctor_info = re.sub(r"(?i)dr\.?\s*", "", doctor_info).strip()
                doctor_info = f"Dr. {doctor_info}"
                pending_appointment['doctor'] = doctor_info
    
            response = f"Perfect! I'll schedule your {pending_appointment.get('department', '').title()} appointment with {doctor_info} for {date}. What time would you prefer? Our available slots are between 9:00 AM to 4:30 PM."

            pending_appointment["date"] = date
            self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_time")
            return {"response": sanitize_response(response)}

            
        elif state == "waiting_for_time":
            time_prompt = ChatPromptTemplate.from_template(
                    """Extract the time from this message and format it as a standard 12-hour time:
                    Message: {message}

                    Return the time in format "HH:MM AM/PM" (e.g., "10:00 AM").
                    If no clear time is provided, return "unknown".
                """
                )

            time_chain = time_prompt | llm | StrOutputParser()

            try:
                requested_time = time_chain.invoke({"message": message}).strip()
                requested_time = re.sub(r'"', '', requested_time)
                
                time_match = re.search(r'(\d{1,2}:\d{2} [AP]M)', requested_time, re.IGNORECASE)
                if not time_match:
                    raise ValueError("Invalid time format")
                
                formatted_time = time_match.group(1).upper()
                pending_date = pending_appointment.get("date", "")
                
                if pending_date in self.booked_appointments:
                    if formatted_time in self.booked_appointments[pending_date]:
                        alternatives = [t for t in self.available_time_slots 
                                      if t not in self.booked_appointments[pending_date]]
                        response = (f"Sorry, {formatted_time} is already booked. "
                                  f"Available times on {pending_date}: {', '.join(alternatives)}")
                        return {"response": response}
                    else:
                        self.booked_appointments[pending_date].append(formatted_time)
                else:
                    self.booked_appointments[pending_date] = [formatted_time]
                
                pending_appointment["time"] = formatted_time
                response = "Great! What phone number should we use to confirm your appointment?"
                self.conversation_tracker.set_pending_appointment(pending_appointment, "waiting_for_phone")
                return {"response": sanitize_response(response)}

            except Exception as e:
                print(f"Error processing time: {e}")
                response = ("I couldn't understand the time. Please choose from our available slots: " 
                          + ", ".join(self.available_time_slots))
                return {"response": response}

        elif state == "waiting_for_phone":
            phone_match = re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', message)
            if phone_match:
                phone_number = phone_match.group(1)
                pending_appointment["phone_number"] = phone_number
                
                confirmation = self._format_appointment_confirmation(pending_appointment)
                self.conversation_tracker.clear_pending_appointment()
                return {
                    "response": sanitize_response(confirmation),
                    "appointment_details": pending_appointment,
                    "appointment_completed": True
                }
            else:
                response = "I didn't catch a valid phone number. Please provide your phone number in any format (e.g. 123-456-7890)."
                return {"response": response}

        else:
            response = "I'm having trouble processing your appointment. Let's start over."
            self.conversation_tracker.clear_pending_appointment()
            return {"response": response}

    def _format_appointment_confirmation(self, details):
        """Format final appointment confirmation message"""
        return (
            f"Appointment confirmed!\n"
            f"Doctor: {details.get('doctor', 'Not specified')}\n"
            f"Department: {details.get('department', 'Not specified')}\n"
            f"Date: {details.get('date', 'Not specified')}\n"
            f"Time: {details.get('time', 'Not specified')}\n"
            f"Phone: {details.get('phone_number', 'Not provided')}\n\n"
            f"A confirmation PDF has been generated. Please arrive 15 minutes early!"
        )

    def analyze_symptoms(self, message):
        """Analyze symptoms in the message and return analysis results"""
        message = message.lower()
        symptoms = []
        severity = "moderate"
        
        symptom_patterns = {
            "headache": ["neurology", "general physician"],
            "migraine": ["neurology"],
            "fever": ["general physician"],
            "cough": ["pulmonology", "general physician"],
            "chest pain": ["cardiology", "emergency"],
            "abdominal pain": ["gastroenterology", "general physician"],
            "rash": ["dermatology"],
            "joint pain": ["orthopedics", "rheumatology"],
            "back pain": ["orthopedics", "physical medicine"],
            "anxiety": ["psychiatry", "general physician"],
            "depression": ["psychiatry"],
            "dizziness": ["neurology", "cardiology"],
            "nausea": ["gastroenterology", "general physician"],
            "vomiting": ["gastroenterology", "general physician"],
            "fatigue": ["general physician", "endocrinology"],
            "shortness of breath": ["pulmonology", "cardiology", "emergency"],
            "swelling": ["general physician", "nephrology"],
            "bleeding": ["hematology", "emergency"],
            "infection": ["infectious disease", "general physician"],
            "allergy": ["allergy", "immunology"],
            "vision problems": ["ophthalmology"],
            "hearing problems": ["ent"],
            "urinary problems": ["urology"],
            "menstrual problems": ["gynecology"]
        }
        
        severity_indicators = {
            "emergency": ["severe", "intense", "unbearable", "emergency", "urgent", "critical", "life-threatening"],
            "high": ["high", "strong", "significant", "persistent", "chronic", "frequent"],
            "moderate": ["moderate", "mild", "occasional", "intermittent"]
        }
        
        for symptom, departments in symptom_patterns.items():
            if symptom in message:
                symptoms.append(symptom)
        
        for level, indicators in severity_indicators.items():
            if any(indicator in message for indicator in indicators):
                severity = level
                break
        
        suggested_departments = set()
        for symptom in symptoms:
            if symptom in symptom_patterns:
                suggested_departments.update(symptom_patterns[symptom])
        
        if not symptoms and any(keyword in message for keyword in ["pain", "ache", "symptom", "feeling", "experiencing"]):
            suggested_departments.add("general physician")
        
        if not suggested_departments:
            suggested_departments.add("general physician")
        
        return {
            "symptoms": symptoms,
            "suggested_departments": list(suggested_departments),
            "severity": severity
        }
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
