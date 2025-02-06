#ver1.1

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # Enable CORS for all routes

# Increase file upload limit to 50 MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ ERROR: OpenRouter API key is missing. Please set it in the environment variables.")

# Initialize OpenAI client
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.base_url = "https://openrouter.ai/api/v1"


# Home route to serve the frontend
@app.route("/")
def home():
    return app.send_static_file("index.html")

# Analyze route to handle file upload and analysis
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Check if the request contains JSON data
        if not request.is_json:
            return jsonify({"error": "Invalid request", "details": "Request must be JSON"}), 400

        # Get the JSON data from the request
        data = request.get_json()
        if "text" not in data:
            return jsonify({"error": "Invalid input", "details": "Missing 'text' field"}), 400

        # Extract and clean the conversation text
        conversation_text = data["text"].strip()
        if not conversation_text:
            return jsonify({"error": "Invalid input", "details": "Empty conversation text"}), 400

        # Analyze the conversation using OpenRouter API
        response = analyze_conversation(conversation_text)
        return jsonify(response)

    except Exception as e:
        print("Unexpected Server Error:", str(e))
        return jsonify({"error": "Unexpected Server Error", "details": str(e)}), 500

# Function to analyze conversation using OpenRouter API
def analyze_conversation(conversation_text):
    try:
        # Trim and limit the length of the text to avoid exceeding model constraints
        cleaned_text = conversation_text.strip()
        if len(cleaned_text) > 2000:  # Adjust as needed
            cleaned_text = cleaned_text[:2000] + " ... (trimmed)"

        print(f"🔹 Sending {len(cleaned_text)} characters to OpenRouter")

        # Send the conversation text to OpenRouter API
        completion = openai.ChatCompletion.create(
            extra_headers={
                "HTTP-Referer": "https://your-website.com",  # Replace with your website URL
                "X-Title": "YourApp",  # Replace with your app name
            },
            model="deepseek/deepseek-r1:free",
            messages=[
                {"role": "system", "content": "Analyze the following conversation and provide structured insights."},
                {"role": "user", "content": cleaned_text}
            ]
        )

        print("✅ OpenRouter Response:", completion)

        # Check if the API response is valid
        if not completion.choices or not completion.choices[0].message.content.strip():
            return {"error": "Empty response from OpenRouter", "details": "Try again with different input."}

        # Return structured analysis results
        return {
            "relationship_type": completion.choices[0].message.content,
            "confidence": 0.95,  # Placeholder value
            "sentiment": "neutral",  # Placeholder value
            "intensity": "medium",  # Placeholder value
            "key_intentions": ["informative"],  # Placeholder value
            "main_topics": ["conversation"]  # Placeholder value
        }

    except Exception as e:
        print("❌ OpenRouter API Error:", str(e))
        return {"error": "API request failed", "details": str(e)}

@app.errorhandler(Exception)
def handle_exception(e):
    print("❌ SERVER ERROR:", traceback.format_exc())
    return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)


