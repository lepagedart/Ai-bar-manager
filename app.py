from flask import Flask, request, render_template, session
from flask_session import Session
from openai import OpenAI
import os
from dotenv import load_dotenv
from rag_retriever import retrieve_codex_context

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
with open("system_prompt.txt", "r") as file:
    system_prompt = file.read()


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Replace with something secure in production
app.config["SESSION_TYPE"] = "filesystem"
Session(app)  # Initialize session support

@app.route("/", methods=["GET", "POST"])
def index():
    cocktail = ""

    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        # Check if this is the first submission with a concept
        if "concept" not in session or not session["concept"]:
            concept = request.form.get("concept", "").strip()
            if concept:
                session["concept"] = concept
            else:
                return render_template("index.html", cocktail="", chat_history=session["chat_history"])

        # Handle new user prompt
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            concept = session.get("concept", "")
            full_prompt = f"Venue concept: {concept}\n\n{prompt}"
            session["chat_history"].append({"role": "user", "content": full_prompt})

            # Send to OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}] + session["chat_history"]
            )

            reply = response.choices[0].message.content
            session["chat_history"].append({"role": "assistant", "content": reply})
            cocktail = reply

    # Always return a response
    return render_template("index.html", cocktail=cocktail, chat_history=session["chat_history"])

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("chat_history", None)
    session.pop("concept", None)
    return render_template("index.html", cocktail="", chat_history=[])


from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

@app.route("/download", methods=["POST"])
def download():
    if "chat_history" not in session or not session["chat_history"]:
        return "No chat history available", 400

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica", 12)
    y = height - 40

    pdf.drawString(30, y, f"Raise the Bar Consulting - AI Session Summary")
    y -= 30

    for message in session["chat_history"]:
        speaker = message["role"].capitalize()
        text = f"{speaker}: {message['content']}"
        for line in text.split("\n"):
            pdf.drawString(30, y, line[:100])  # basic line wrapping
            y -= 15
            if y < 40:
                pdf.showPage()
                y = height - 40

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="raise_the_bar_ai_summary.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)