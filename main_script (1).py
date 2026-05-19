import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import openai
import streamlit as st
from openai import OpenAI

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Email configuration (use environment variables for safety)
SMTP_SERVER = st.secrets.get("SMTP_SERVER")
SMTP_PORT = st.secrets.get("SMTP_PORT")
SMTP_USERNAME = st.secrets.get("SMTP_USERNAME")
SMTP_PASSWORD = st.secrets.get("SMTP_PASSWORD")

# Streamlit UI setup
st.set_page_config(page_title="Trauma Presentation Feeback Bot", page_icon="🩺", layout="centered")
st.title("🩺 Trauma Presentation Feeback Bot")
st.markdown("Record or upload a presentation to receive AI-based feedback, edit it, and send to your student.")
st.warning(
    "⚠️ Do not present Personal Health Information (PHI) or patient identifying features in the presentation."
)

if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = None

# Audio input
audio_file = st.audio_input("🎙️ Record or upload your presentation (max ~2 min recommended):")

if audio_file:
    st.info("Processing your presentation... Please wait.")

    try:
        # Transcribe using OpenAI
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file
        )

        transcribed_text = transcript.text

        st.success("✅ Transcription complete.")

        st.subheader("📋 Transcript:")
        st.text_area(
            "Transcribed Text",
            transcribed_text,
            height=200
        )

        st.info("Generating feedback from Dr. Al...")

        messages = [
            {
                "role": "system",
                "content": """
You are Dr. Al, an expert trauma surgeon educator.

Provide supportive ATLS-style feedback on trauma presentations.

Score:
1. Structure & Organization
2. History Taking
3. Primary Survey
4. Secondary Survey
5. Treatment Plan
6. Communication
7. Clinical Reasoning
8. Time Management

Provide:
- strengths
- areas for improvement
- total score out of 40
- short summary
"""
            },
            {
                "role": "user",
                "content": transcribed_text
            }
        ]

        completion = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=messages,
            temperature=0
        )

        import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import openai
import streamlit as st
from openai import OpenAI

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Email configuration (use environment variables for safety)
SMTP_SERVER = st.secrets.get("SMTP_SERVER")
SMTP_PORT = st.secrets.get("SMTP_PORT")
SMTP_USERNAME = st.secrets.get("SMTP_USERNAME")
SMTP_PASSWORD = st.secrets.get("SMTP_PASSWORD")

# Streamlit UI setup
st.set_page_config(page_title="Trauma Presentation Feeback Bot", page_icon="🩺", layout="centered")
st.title("🩺 Trauma Presentation Feeback Bot")
st.markdown("Record or upload a presentation to receive AI-based feedback, edit it, and send to your student.")
st.warning(
    "⚠️ Do not present Personal Health Information (PHI) or patient identifying features in the presentation."
)

if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = None

# Audio input
audio_file = st.audio_input("🎙️ Record or upload your presentation (max ~2 min recommended):")

if audio_file:
    st.info("Processing your presentation... Please wait.")

    try:
        # Transcribe using OpenAI
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file
        )

        transcribed_text = transcript.text

        st.success("✅ Transcription complete.")

        st.subheader("📋 Transcript:")
        st.text_area(
            "Transcribed Text",
            transcribed_text,
            height=200
        )

        st.info("Generating feedback from Dr. Al...")

        messages = [
            {
                "role": "system",
                "content": """
You are Dr. Al, an expert trauma surgeon educator.

Provide supportive ATLS-style feedback on trauma presentations.

Score:
1. Structure & Organization
2. History Taking
3. Primary Survey
4. Secondary Survey
5. Treatment Plan
6. Communication
7. Clinical Reasoning
8. Time Management

Provide:
- strengths
- areas for improvement
- total score out of 40
- short summary
"""
            },
            {
                "role": "user",
                "content": transcribed_text
            }
        ]

        completion = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=messages,
            temperature=0
        )

        st.session_state.ai_feedback = (
            completion.choices[0].message.content
        )

        st.success("✅ Feedback generated.")

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

        st.subheader("💬 Review and Edit Feedback")
        edited_feedback = st.text_area(
            "Faculty can edit or add comments below before sending:",
            value=st.session_state.ai_feedback,  # <-- use session_state here
            height=300,
            key="feedback_area"
        )
        st.session_state.edited_feedback = edited_feedback  
        
        # Email section
        st.subheader("✉️ Send Feedback to Student")
        col1, col2 = st.columns(2)
        with col1:
            student_email = st.text_input("Student Email(s) (comma separated)")
            cc_emails = st.text_input("CC Email(s) (optional, comma separated)")
        with col2:
            faculty_name = st.text_input("Faculty Name (optional)")
            student_name = st.text_input("Student Name (optional)")

        email_subject = st.text_input("Email Subject", "Trauma Hand-Off Presentation Feedback")
        send_email = st.button("📤 Send Feedback via Email")

        if send_email:
            if not student_email:
                st.warning("Please enter the student's email address.")
            elif not SMTP_USER or not SMTP_PASSWORD:
                st.error("Email sending is not configured. Please set SMTP_USER and SMTP_PASSWORD in your .env file.")
            else:
                try:
                    # Split and clean addresses
                    to_addresses = [email.strip() for email in student_email.split(",") if email.strip()]
                    cc_addresses = [email.strip() for email in cc_emails.split(",") if email.strip()]
                    all_recipients = to_addresses + cc_addresses
        
                    # Compose email
                    msg = MIMEMultipart()
                    msg["From"] = SMTP_USER
                    msg["To"] = ", ".join(to_addresses)
                    msg["Cc"] = ", ".join(cc_addresses)
                    msg["Subject"] = email_subject

                    if student_name:
                        body = f"Dear {student_name},\n\nHere is your Trauma Hand-Off Presentation and feedback:\n\n"
                    else:
                        body = f"Dear Student,\n\nHere is your Trauma Hand-Off Presentation feedback:\n\n"

                    body += f"--- Student Presentation Transcript ---\n{transcribed_text}\n\n"
                    body += f"--- Feedback ---\n{st.session_state.edited_feedback}\n\n"
                    
                    if faculty_name:
                        body += f"Best regards,\n{faculty_name}"
                    else:
                        body += "Best regards,\nTrauma Faculty"
        
                    msg.attach(MIMEText(body, "plain"))
        
                    # Send email
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(SMTP_USER, SMTP_PASSWORD)
                        server.send_message(msg, from_addr=SMTP_USER, to_addrs=all_recipients)
        
                    st.success(f"✅ Feedback successfully sent to: {', '.join(all_recipients)}!")
        
                except Exception as e:
                    st.error(f"An error occurred while sending the email: {e}")

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
else:
    st.info("👆 Please record or upload your trauma hand-off presentation to begin.") 
        
        # Email section
        st.subheader("✉️ Send Feedback to Student")
        col1, col2 = st.columns(2)
        with col1:
            student_email = st.text_input("Student Email(s) (comma separated)")
            cc_emails = st.text_input("CC Email(s) (optional, comma separated)")
        with col2:
            faculty_name = st.text_input("Faculty Name (optional)")
            student_name = st.text_input("Student Name (optional)")

        email_subject = st.text_input("Email Subject", "Trauma Hand-Off Presentation Feedback")
        send_email = st.button("📤 Send Feedback via Email")

        if send_email:
            if not student_email:
                st.warning("Please enter the student's email address.")
            elif not SMTP_USER or not SMTP_PASSWORD:
                st.error("Email sending is not configured. Please set SMTP_USER and SMTP_PASSWORD in your .env file.")
            else:
                try:
                    # Split and clean addresses
                    to_addresses = [email.strip() for email in student_email.split(",") if email.strip()]
                    cc_addresses = [email.strip() for email in cc_emails.split(",") if email.strip()]
                    all_recipients = to_addresses + cc_addresses
        
                    # Compose email
                    msg = MIMEMultipart()
                    msg["From"] = SMTP_USER
                    msg["To"] = ", ".join(to_addresses)
                    msg["Cc"] = ", ".join(cc_addresses)
                    msg["Subject"] = email_subject

                    if student_name:
                        body = f"Dear {student_name},\n\nHere is your Trauma Hand-Off Presentation and feedback:\n\n"
                    else:
                        body = f"Dear Student,\n\nHere is your Trauma Hand-Off Presentation feedback:\n\n"

                    body += f"--- Student Presentation Transcript ---\n{transcribed_text}\n\n"
                    body += f"--- Feedback ---\n{st.session_state.edited_feedback}\n\n"
                    
                    if faculty_name:
                        body += f"Best regards,\n{faculty_name}"
                    else:
                        body += "Best regards,\nTrauma Faculty"
        
                    msg.attach(MIMEText(body, "plain"))
        
                    # Send email
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(SMTP_USER, SMTP_PASSWORD)
                        server.send_message(msg, from_addr=SMTP_USER, to_addrs=all_recipients)
        
                    st.success(f"✅ Feedback successfully sent to: {', '.join(all_recipients)}!")
        
                except Exception as e:
                    st.error(f"An error occurred while sending the email: {e}")

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
else:
    st.info("👆 Please record or upload your trauma hand-off presentation to begin.")
