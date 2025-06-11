import os
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from dotenv import load_dotenv
from openai import OpenAI
from rag_retriever import retrieve_codex_context
from utils import generate_pdf, send_email

load_dotenv()

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure OpenRouter client (Meta LLaMA)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    conversation = session.get("conversation", [])

    if request.method == "POST":
        venue = request.form.get("concept", "")
        user_prompt = request.form.get("user_prompt", "")
        email = request.form.get("email", "")

        # Add user message
        conversation.append({"role": "user", "content": f"Venue concept: {venue}\n{user_prompt}"})

        # Inject RAG reference
        rag_context = retrieve_codex_context(user_prompt)
        conversation.insert(-1, {"role": "system", "content": f"Helpful reference:\n{rag_context}"})

        # Load system prompt
        with open("system_prompt.txt", "r") as file:
            system_prompt = file.read()

        # Generate response from LLaMA
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-8b-instruct:free",
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation
            ]
        )
        result = response.choices[0].message.content.strip()

        # Save response
        conversation.append({"role": "assistant", "content": result})
        session["conversation"] = conversation

        # Optional: Email + PDF
        if email:
            generate_pdf(result)
            send_email(email, "Raise the Bar - Cocktail Response", result)

    return render_template("index.html", result=result, conversation=conversation)

@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)