from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import smtplib
from email.message import EmailMessage

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect("submissions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class Submission(BaseModel):
    name: str
    email: str
    message: str

@app.post("/submit")
def submit_form(data: Submission):
    conn = sqlite3.connect("submissions.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO submissions (name, email, message) VALUES (?, ?, ?)", 
                   (data.name, data.email, data.message))
    conn.commit()
    conn.close()

    try:
        send_email(data.name, data.email, data.message)
    except Exception as e:
        print(f"Email failed: {e}")

    return {"message": "Data received and email sent!"}

def send_email(name, to_email, msg_content):
    EMAIL_ADDRESS = "your.email@gmail.com"
    EMAIL_PASSWORD = "your_app_password"

    msg = EmailMessage()
    msg["Subject"] = "EcoPilot Form Confirmation"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(f"Hi {name},\n\nThanks for your submission:\n\n{msg_content}\n\n- EcoPilot Team")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# ✅ NEW: EcoScore Endpoint
@app.post("/ecoscore")
def get_eco_score(data: dict):
    text = data.get("text", "").lower()
    score = 100
    if "plastic" in text:
        score -= 20
    if "shipped from abroad" in text or "air" in text:
        score -= 30
    if "eco" in text or "sustainable" in text:
        score += 10
    return {"score": max(0, min(score, 100))}
