from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.startswith("sk-or-v1-"):
    raise ValueError("❌ ERROR: Please set a valid OpenRouter API key in environment variables.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

@app.route("/")
def home():
    return "Chat Analysis API is Running!"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid request", "details": "Request must be JSON"}), 400
        
        data = request.get_json()
        if "conversation" not in data:
            return jsonify({"error": "Invalid input", "details": "Missing 'conversation' field"}), 400

        conversation_text = data["conversation"].strip()
        if not conversation_text:
            return jsonify({"error": "Invalid input", "details": "Empty conversation text"}), 400

        response = analyze_conversation(conversation_text)
        return jsonify(response)
    
    except Exception as e:
        print("Unexpected Server Error:", str(e))
        return jsonify({"error": "Unexpected Server Error", "details": str(e)}), 500

# Function to analyze conversation
def analyze_conversation(conversation_text):
    try:
        print("🔵 Sending request to OpenRouter...")
        
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {"role": "system", "content": "Analyze the following conversation."},
                {"role": "user", "content": conversation_text}
            ]
        )

        print("✅ OpenRouter Response:", completion)

        return {
            "relationship_type": completion.choices[0].message.content,
            "confidence": 0.95,
            "sentiment": "neutral",
            "intensity": "medium",
            "key_intentions": ["informative"],
            "main_topics": ["conversation"]
        }

    except Exception as e:
        print("❌ OpenRouter API Error:", str(e))
        return {"error": "API request failed", "details": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))  # Default to 3000 for Coolify
    app.run(host="0.0.0.0", port=port, debug=False)
