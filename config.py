import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

    # Groq AI
    GROQ_API_KEY=os.getenv('GROQ_API_KEY')
    GROQ_MODEL='llama-3.1-8b-instant'

    # COMPANY Details
    COMPANY_NAME = 'City Care Clinic'
    AGENT_NAME = 'CAREBOOK AI'

    # Services
    SERVICES = [
        "General Checkup",
        "Dental Consultation",
        "Eye Examination",
        "Blood Test"
    ]

    # Available time slots
    TIME_SLOTS = [
        "09:00 AM", "10:00 AM", "11:00 AM", "12:00 AM",
        "02:00 PM", "02:00 PM", "04:00 PM", "05:00 PM" 
    ]

    # Working days
    WORKING_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                    "Friday", "saturday"]
    
    # Appointment settings
    REMINDER_HOURS_BEFORE = 1
    MAX_APPOINTMENT_PER_SLOT = 1