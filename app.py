from flask import Flask, request, render_template, session, send_file
from flask_session import Session
import openai
import os
import io
from dotenv import load_dotenv
from rag_retriever import retrieve_codex_context
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.message import EmailMessage

# Load environment variables
load_dotenv()

# Configure OpenRouter API
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.base_url = "https://openrouter.ai/api/v1"

# Load system prompt from file
with open("system_prompt.txt", "r") as file:
    system_prompt = file.read()

# Initialize Flask app and session
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
def index():
    cocktail = ""

    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        # Set venue concept if not already defined
        if "concept" not in session or not session["concept"]:
            concept = request.form.get("concept", "").strip()
            if concept:
                session["concept"] = concept
            else:
                return render_template("index.html", cocktail="", chat_history=session["chat_history"])

        # Handle prompt
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            concept = session.get("concept", "")
            context = retrieve_codex_context(prompt)

            full_prompt = f"""Venue Concept: {concept}

Relevant context from Cocktail Codex:
{context}

User Prompt:
{prompt}
"""
            session["chat_history"].append({"role": "user", "content": full_prompt})

            response = openai.ChatCompletion.create(
                model="meta-llama/llama-3-8b-instruct",
                messages=[{"role": "system", "content": system_prompt}] + session["chat_history"]
            )

            reply = response.choices[0].message.content
            session["chat_history"].append({"role": "assistant", "content": reply})
            cocktail = reply

    return render_template("index.html", cocktail=cocktail, chat_history=session["chat_history"])

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("chat_history", None)
    session.pop("concept", None)
    return render_template("index.html", cocktail="", chat_history=[])

@app.route("/download", methods=["POST"])
def download():
    if "chat_history" not in session or not session["chat_history"]:
        return "No chat history available", 400

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    pdf.setFont("Helvetica", 12)
    pdf.drawString(30, y, "Raise the Bar Consulting - AI Session Summary")
    y -= 30

    for msg in session["chat_history"]:
        speaker = msg["role"].capitalize()
        for line in f"{speaker}: {msg['content']}".split("\n"):
            pdf.drawString(30, y, line[:100])
            y -= 15
            if y < 40:
                pdf.showPage()
                y = height - 40

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="raise_the_bar_ai_summary.pdf", mimetype="application/pdf")

@app.route("/email", methods=["POST"])
def email():
    if "chat_history" not in session or not session["chat_history"]:
        return "No chat history available", 400

    recipient_email = request.form.get("email", "").strip()
    if not recipient_email:
        return "Email address is required", 400

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    pdf.setFont("Helvetica", 12)
    pdf.drawString(30, y, "Raise the Bar Consulting - AI Session Summary")
    y -= 30

    for msg in session["chat_history"]:
        speaker = msg["role"].capitalize()
        for line in f"{speaker}: {msg['content']}".split("\n"):
            pdf.drawString(30, y, line[:100])
            y -= 15
            if y < 40:
                pdf.showPage()
                y = height - 40

    pdf.save()
    buffer.seek(0)

    msg = EmailMessage()
    msg["Subject"] = "Raise the Bar - AI Session Summary"
    msg["From"] = os.getenv("SMTP_FROM_EMAIL")
    msg["To"] = recipient_email
    msg.set_content("Attached is the PDF summary of your session with Raise the Bar AI Bar Manager.")
    msg.add_attachment(buffer.read(), maintype="application", subtype="pdf", filename="raise_the_bar_ai_summary.pdf")

    try:
        with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)