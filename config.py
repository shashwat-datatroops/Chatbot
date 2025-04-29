DEPARTMENTS = [
    "cardiology", "dermatology", "neurology", "orthopedics", 
    "pediatrics", "psychiatry", "radiology", "surgery",
    "oncology", "gynecology", "urology", "ent", "ophthalmology",
    "general physician"
]

PROCEDURES = [
    "checkup", "vaccination", "physical", "blood test", "x-ray",
    "mri", "ct scan", "ultrasound", "ecg", "colonoscopy",
    "liposuction", "consultation", "screening", "therapy"
]

DOCTORS = {
    "cardiology": ["Dr. Smith", "Dr. Johnson", "Dr. Williams"],
    "dermatology": ["Dr. Davis", "Dr. Miller", "Dr. Wilson"],
    "neurology": ["Dr. Moore", "Dr. Taylor", "Dr. Anderson"],
    "orthopedics": ["Dr. Thomas", "Dr. Jackson", "Dr. White"],
    "pediatrics": ["Dr. Harris", "Dr. Martin", "Dr. Thompson"],
    "psychiatry": ["Dr. Garcia", "Dr. Martinez", "Dr. Robinson"],
    "radiology": ["Dr. Clark", "Dr. Rodriguez", "Dr. Lewis"],
    "surgery": ["Dr. Lee", "Dr. Walker", "Dr. Hall"],
    "oncology": ["Dr. Allen", "Dr. Young", "Dr. Hernandez"],
    "gynecology": ["Dr. King", "Dr. Wright", "Dr. Lopez"],
    "urology": ["Dr. Hill", "Dr. Scott", "Dr. Green"],
    "ent": ["Dr. Adams", "Dr. Baker", "Dr. Gonzalez"],
    "ophthalmology": ["Dr. Nelson", "Dr. Carter", "Dr. Mitchell"],
    "general physician": ["Dr. Brown", "Dr. Wilson", "Dr. Taylor"]
}

AVAILABLE_TIME_SLOTS = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
    "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
    "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM",
    "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"
]

REPORTS_METADATA = [
    {
        "file_path": "reports/blood_test_june_2023.pdf",
        "date": "2023-06-15",
        "type": "blood_test",
        "phone_number": "1234567890"
    },
    {
        "file_path": "reports/sugar_test_august_2022.pdf",
        "date": "2022-08-20",
        "type": "sugar_test",
        "phone_number": "1234567890"
    }
]

BOOKED_APPOINTMENTS = {
    "April 23, 2025": ["10:00 AM", "02:30 PM"],
    "April 24, 2025": ["09:30 AM", "11:00 AM", "03:00 PM"]
}