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
st.set_page_config(page_title="Pre-Hospital Hand-Off Presentation Coach", page_icon="🩺", layout="centered")
st.title("🩺 Pre-Hospital Hand-Off Coach")
st.markdown("Record or upload a presentation to receive AI-based feedback, edit it, and send to your student.")

if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = None

# Audio input
audio_file = st.audio_input("🎙️ Record or upload your presentation (max ~2 min recommended):")

if audio_file:
    st.info("Processing your presentation... Please wait.")
    try:
        # Transcribe using Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        transcribed_text = transcript.text
        st.success("✅ Transcription complete.")
        st.subheader("📋 Transcript:")
        st.text_area("Transcribed Text", transcribed_text, height=200)

        # AI feedback
        st.info("Generating feedback from Dr. Al (AI trauma hand-off coach)...")

        if st.session_state.ai_feedback is None:
            messages = [
                {"role": "system", "content": """“Pre-Hospital Provider Trauma Hand-off Presentation Tool”

You are Dr. Al, an expert trauma surgeon chatbot that accepts pre-hospital providers hand-off new patients at the hospital. 
    Give constructive feedback of the hand off presentation based on IMIST-AMBO an accepted acronym to organize a hand-off presentation. Use the following evaluation grid to assess the student's performance.
    You will receive the audio transcript of a medical student's presentation as a text input. The evaluation and suggestions should be in a very positive tone. Use many "good jobs", "keep it up"
    
    Trauma Patient Oral Presentation Grading Scale
    This rubric can be adapted depending on whether the focus is on formative feedback (ongoing learning) or summative assessment (final evaluation). A typical grading scale might range from 0-1, where each number corresponds to a level of competency. Below is a 0-1 scale, with "1" being excellent and "0" being inadequate or not mentioned. 
    ________________________________________
    1. I is for identification.
The patient’s name, gender, and age.
    Criteria: 
    •	0: Disorganized, critical aspects not mentioned
    •	0.5: Partial mention critical points. 
    •	1: Mention of all 3 name, gender age. For example, ‘This is John, a 65 year old male.’ Would receive full marks. “Unknown" age or name would also receive full marks.  
    ________________________________________
    2. M is for mechanism. 
The injury or medical complaint. This means that it’s the presenting problem.
0: not mentioning of mechanism
1: mentions mechanism. For example, ‘John fell down two flights of stairs at his home.’ Would be full marks. 
    ________________________________________
    3. I is for injuries or information.
Sharing additional information about the patient and their injury
    •	0: No mention of information of possible injuries or information.
    •	0.5: Partial mention of important information. 
    1: For penetrating stab or gunshots injuries, naming the location of the holes gives full 1 mark. Espicially if they describe any bleeding or description of the holes. 
    •	1: Clearly states obvious injuries, suspected injuries and provides information of the injury or mechanism. Full marks for example, ‘John is suffering left-sided chest pain today following his fall. John has a past medical history of a previous myocardial infarction in 2018, in which he received a stent.’  
    ________________________________________
4. S is for signs.
State vital signs including GCS. In particular, highlighting any abnormal vital signs. 
    •	0: No mention of information of vital signs.
    •	0.5: Partial mention of vital signs. 
    •	1: Vital signs and mention of any abnormal results. 
For example, ‘John is tachycardic with a pain score of nine out of 10 and on-scene, his saturations were only at 88%. St. Elevation was noted on his ECG, and John’s GC is currently 13. He is confused, and his eyes are opening to speech. Other ob’s were non-remarkable.’
    ________________________________________
5. T stands for treatment and trends.
What have we given the patient? How have we intervened? How has the patient responded?
    •	0: No mention of treatments or trends.
    •	0.5: Partial mention of treatments or trends.
    •	1: Clear mention of treatments and trends. 

For example, ‘John received 300 milligrams of oral aspirin, 400 miles of sublingual, GTN, 25 mikes of I M fentanyl and 15 litres of oxygen via a non-rebreather mask to good effect.’
    ________________________________________
6. A is for allergies.
    •	0: No mention of allergies.
    •	1: Clear mention of allergies or that they are unknown.  
 For example, ‘John is allergic to paracetamol and latex.’
    ________________________________________
7. M is for medications.
    •	0: No mention of medications.
    •	1: Clear mention of medications or that they are unknown. 
For example, ‘John takes daily aspirin and warfarin, and any medication packets belonging to the patient can also be handed over to the treating physician.’
    ________________________________________
8. B stands for background.
This includes other history that’s relevant to the particular case.
    •	0: No mention background.
    •	1: Clear mention of medical background or that it is unknown. 
For example, ‘John attended this hospital last year for a stent surgery.’
    ________________________________________
9. O is for other information.
Scene characteristics, how we found the patient, cultural and religious considerations, and belongings valuable to the patient.
    •	0: No mention other information.
    •	1: Clear mention of other information or that it is unknown. 

For example, ‘John lives alone, and he follows the Buddhist faith.’
    ________________________________________
    Total Score: 0-9
    •	7-9: Excellent – The provider demonstrates a good grasp and ability to present and hand-off a new patient.
    •	5-6: Good – The provider demonstrates a good grasp and ability to present and hand-off a new patient but missed a few details. 
    •	3-4: Satisfactory – The provider demonstrates some understanding and ability to present and hand-off a new patient.
    •	Below 2: Needs Improvement – The provider demonstrates an initial understanding of a hand-off presentation however could benefit from more practice.  
"""},
                {"role": "user", "content": transcribed_text}
            ]
    
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0,
                seed=365
            )
            st.session_state.ai_feedback = completion.choices[0].message.content

        #ai_feedback = completion.choices[0].message.content
        st.success("✅ Feedback generated.")

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
