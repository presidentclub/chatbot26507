from flask import Flask, render_template, request, session, jsonify
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secret key for session storage
app.secret_key = os.urandom(24)

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-05-01-preview"
)

@app.route("/", methods=["GET"])
def home():
    if "history" not in session:
        session["history"] = []
    return render_template("index.html", history=session["history"])

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form["message"]

    history = session.get("history", [])

    # Call Azure OpenAI
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )

    ai_reply = response.choices[0].message.content

    # Save history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": ai_reply})
    session["history"] = history

    return jsonify({
        "user": user_message,
        "ai": ai_reply
    })

@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
