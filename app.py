from flask import Flask, render_template, request, session
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secret key for session storage
app.secret_key = os.urandom(24)

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-05-01-preview"
)

@app.route("/", methods=["GET"])
def home():
    # Initialize chat history if not existing
    if "history" not in session:
        session["history"] = []
    return render_template("index.html", history=session["history"])

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.form["message"]
        print(f"USER MESSAGE RECEIVED: {user_message}")

        # Get existing history
        history = session.get("history", [])

        # Add user message to history
        history.append({"role": "You", "message": user_message})

        print("Calling Azure OpenAI...")

        # Call Azure OpenAI
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        ai_reply = response.choices[0].message.content
        print(f"AI REPLY: {ai_reply}")

        # Add AI reply to history
        history.append({"role": "AI", "message": ai_reply})

        # Save back to session
        session["history"] = history

        return render_template("index.html", history=history)

    except Exception as e:
        # THIS IS CRITICAL FOR DEBUGGING IN AZURE
        print(f"ERROR IN /chat ROUTE: {str(e)}")

        # Show a readable error instead of blank 500
        return f"ERROR: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
