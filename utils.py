import re
import fitz

def sanitize_response(response):
    """Clean and format responses professionally"""
    if not response:
        return "I'm sorry, I couldn't process that request."
    
    response = re.sub(r"(?i)(extracted department|department from the user's message is|the name of the doctor in the message is)", "", response)
    response = re.sub(r"\b(?:department:|doctor:|date:)\s*", "", response, flags=re.IGNORECASE)
    
    response = re.sub(r"^(Mixtral\s*\d+:|LLM:|Bot:|Assistant:).*?([A-Z])", r"\2", response, flags=re.DOTALL)

    response = re.sub(r"(?i)from the provided message.*?return only", "", response)
    response = re.sub(r"(?i)as per your instructions.*?provide you with", "", response)
    response = re.sub(r'"([^"]+)"', r'\1', response)

    response = re.sub(r"^(Mixtral\s*\d+:|LLM:|Bot:|Assistant:)\s*", "", response)
    response = re.sub(r"(?i)the medical department from the user's message is:", "", response)

    response = re.sub(r"(?i) dr\.?", " Dr. ", response)
    response = re.sub(r"\b(ent)\b", lambda m: m.group(1).upper(), response)
    response = re.sub(r"\b(i|i'm|id)\b", lambda m: m.group(1).capitalize(), response)

    response = re.sub(r"(\d{1,2})(\d{2})\s?(am|pm)", 
                lambda m: f"{m.group(1)}:{m.group(2)} {m.group(3).upper()}", response)

    sentences = [s.strip().capitalize() for s in re.split(r'[.!?]', response) if s]
    response = '. '.join(sentences) + ('' if response.endswith('.') else '.')

    response = re.sub(r"\s{2,}", " ", response)
    return response.strip()

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE)
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""