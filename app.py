import os
import uuid
from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
from flask_session import Session
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load .env
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# FAISS and Embedding Model
VECTOR_INDEX_PATH = "codex_faiss_index"
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(
    VECTOR_INDEX_PATH,
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

# RAG context retriever
def retrieve_codex_context(prompt):
    docs = vectorstore.similarity_search(prompt, k=3)
    return "\n\n".join(doc.page_content for doc in docs)

# PDF generator
def generate_pdf(text, filename="response.pdf"):
    path = os.path.join("static", filename)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 50
    for line in text.split("\n"):
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()
    return path

# Email sender
def send_email_with_attachment(to_email, subject, body, file_path):
    msg = MIMEMultipart()
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))
    with open(file_path, "rb") as file:
        part = MIMEApplication(file.read(), _subtype="pdf")
        part.add_header("Content-Disposition", "attachment", filename=os.path.basename(file_path))
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            prompt = request.form.get("prompt", "").strip()
            email = request.form.get("email", "").strip()

            if not prompt:
                flash("Prompt cannot be empty.", "warning")
                return render_template("index.html")

            context = retrieve_codex_context(prompt)

            filename = f"cocktail_response_{uuid.uuid4().hex}.pdf"
            pdf_path = generate_pdf(context, filename)

            if email:
                send_email_with_attachment(email, "Your Custom Cocktail Report", "See attached.", pdf_path)
                flash("📧 Email sent with PDF attached.", "success")
            else:
                session["pdf_path"] = pdf_path
                flash("📄 PDF generated.", "info")

            return render_template("index.html", response=context, pdf_link=url_for("download_pdf"))

        except Exception as e:
            print("🔥 Exception occurred:", e)  # Log to terminal
            flash(f"Error: {str(e)}", "danger")
            return render_template("index.html")

    return render_template("index.html")

@app.route("/download")
def download_pdf():
    path = session.get("pdf_path")
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    flash("No PDF to download.", "warning")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)