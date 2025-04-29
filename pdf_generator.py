import os
import fitz
from datetime import datetime

class PDFGenerator:
    """Simple PDF generator for reports and receipts"""
    def __init__(self):
        self.output_dir = "output"
        self.reports_dir = "reports"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        self._create_sample_reports()
        
    def generate_appointment_pdf(self, appointment_details):
        """Generate a PDF for appointment confirmation"""
        filename = f"{self.output_dir}/appointment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, "w") as f:
            f.write("APPOINTMENT CONFIRMATION\n")
            f.write("=======================\n\n")
            f.write(f"Doctor: {appointment_details.get('doctor', 'Not specified')}\n")
            f.write(f"Date: {appointment_details.get('date', 'Not specified')}\n")
            f.write(f"Time: {appointment_details.get('time', 'Not specified')}\n")
            f.write(f"Department: {appointment_details.get('department', 'Not specified')}\n")
            f.write(f"Procedure: {appointment_details.get('procedure', 'Not specified')}\n")
            f.write(f"Phone Number: {appointment_details.get('phone_number', 'Not provided')}\n")
            f.write("\nPlease arrive 15 minutes before your appointment.\n")
            f.write("Bring your insurance card and ID.\n")
            
        print(f"Generated appointment PDF: {filename}")
        return filename
        
    def generate_report(self, conversation_history):
        """Generate a PDF report of the conversation"""
        filename = f"{self.output_dir}/conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, "w") as f:
            f.write("CONVERSATION REPORT\n")
            f.write("==================\n\n")
            
            for msg in conversation_history:
                sender = "User" if msg["sender"] == "user" else "Bot"
                f.write(f"{msg['timestamp']} - {sender}:\n")
                f.write(f"{msg['content']}\n\n")
                
        print(f"Generated conversation report: {filename}")
        return filename

    def _create_sample_reports(self):
        """Create sample report PDFs if they don't exist"""            
        if not os.path.exists("reports/blood_test_june_2023.pdf"):
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), 
                "Blood Test Report - 15 June 2023\nPatient Name: John Doe\n"
                "Hemoglobin: 13.5 g/dL\nRBC Count: 4.7 million/mcL\n"
                "WBC Count: 6,000 /mcL\nPlatelets: 250,000 /mcL\n"
                "Comments: All blood parameters are within normal range."
            )
            doc.save("reports/blood_test_june_2023.pdf")
            doc.close()
            
        if not os.path.exists("reports/sugar_test_august_2022.pdf"):
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50),
                "Sugar Test Report - 20 August 2022\nPatient Name: John Doe\n"
                "Fasting Blood Sugar: 95 mg/dL\nPostprandial Blood Sugar: 130 mg/dL\n"
                "HbA1c: 5.4%\nComments: Sugar levels are normal. No signs of diabetes."
            )
            doc.save("reports/sugar_test_august_2022.pdf")
            doc.close()