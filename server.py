import os
import json
import re
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
DATA_FILE = 'data.json'
UPLOAD_FOLDER = 'uploads'
EXPERTS = {}

def load_experts_from_env():
    """Loads LLM expert configurations from environment variables."""
    global EXPERTS
    experts_config = {}
    for key, value in os.environ.items():
        match = re.match(r"LLM_(\d+)_NAME", key)
        if match:
            index = match.group(1)
            name = value
            endpoint = os.getenv(f"LLM_{index}_ENDPOINT")
            api_key = os.getenv(f"LLM_{index}_KEY")
            # Get the optional model name, fallback to the display name if not provided
            model_name = os.getenv(f"LLM_{index}_MODEL_NAME", name)

            if name and endpoint and api_key:
                experts_config[name] = {
                    "endpoint": endpoint,
                    "api_key": api_key,
                    "model_name": model_name
                }
    EXPERTS = experts_config
    if not EXPERTS:
        print("Warning: No LLM experts configured. Please set LLM_1_NAME, LLM_1_ENDPOINT, and LLM_1_KEY environment variables.")
    else:
        print(f"Loaded experts: {list(EXPERTS.keys())}")

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Load experts on startup
load_experts_from_env()

# --- Opportunity Search API ---

@app.route('/api/search_opportunities', methods=['POST'])
def search_opportunities():
    """Searches the sam.gov API for opportunities."""
    sam_api_key = os.getenv("SAM_API_KEY")
    if not sam_api_key:
        return jsonify({"error": "SAM.gov API key is not configured on the server."}), 500

    data = request.get_json()
    keywords = data.get('keywords', '')
    postedFrom = data.get('postedFrom')
    postedTo = data.get('postedTo')

    if not postedFrom or not postedTo:
        return jsonify({"error": "A date range (postedFrom and postedTo) is required."}), 400

    params = {
        "api_key": sam_api_key,
        "limit": 50,
        "postedFrom": postedFrom,
        "postedTo": postedTo,
        "title": keywords # Search keywords in the title
    }

    try:
        response = requests.get("https://api.sam.gov/opportunities/v2/search", params=params, timeout=30)
        response.raise_for_status()
        return jsonify(response.json().get("opportunitiesData", []))
    except requests.exceptions.RequestException as e:
        print(f"Error calling SAM.gov API: {e}")
        return jsonify({"error": f"Failed to connect to the SAM.gov API: {e}"}), 502
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred on the server."}), 500

# --- Document Store API ---

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handles file uploads."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        return jsonify({"success": True, "filename": filename, "path": f"/{UPLOAD_FOLDER}/{filename}"}), 201

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serves an uploaded file."""
    return send_from_directory(UPLOAD_FOLDER, filename)


# --- Data Persistence API ---

@app.route('/api/data', methods=['GET'])
def load_data():
    """Loads application state from data.json."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return jsonify(json.load(f))
        else:
            # Return a default structure if the file doesn't exist
            return jsonify({
                "budget": {"spent": 0, "remaining": 100000},
                "deadlines": [],
                "reportText": "",
                "chatHistory": [],
                "documents": []
            })
    except Exception as e:
        print(f"Error loading data: {e}")
        return jsonify({"error": "Could not load data."}), 500

@app.route('/api/data', methods=['POST'])
def save_data():
    """Saves application state to data.json."""
    try:
        data = request.get_json()
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return jsonify({"success": True, "message": "Data saved successfully."})
    except Exception as e:
        print(f"Error saving data: {e}")
        return jsonify({"error": "Could not save data."}), 500

# --- Static File and Chat API ---

@app.route('/')
def index():
    return send_from_directory('.', 'sbir_agent.html')

@app.route('/api/experts', methods=['GET'])
def get_experts():
    """Returns the names of the configured LLM experts."""
    return jsonify(list(EXPERTS.keys()))

@app.route('/api/chat', methods=['POST'])
def chat_handler():
    data = request.get_json()
    if not data or 'messages' not in data or 'model' not in data:
        return jsonify({"error": "Invalid request body. 'messages' and 'model' keys are required."}), 400

    expert_name = data['model']
    expert = EXPERTS.get(expert_name)

    if not expert:
        return jsonify({"error": f"Expert '{expert_name}' not found or not configured on the server."}), 404

    # Prepare the request for the external LLM API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {expert["api_key"]}'
    }

    payload = {
        "model": expert["model_name"], # Use the specific model name for the downstream API
        "messages": data["messages"]
    }

    # Forward the request and handle potential errors
    try:
        response = requests.post(expert["endpoint"], headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error calling LLM API for expert '{expert_name}': {e}")
        return jsonify({"error": f"Failed to connect to the LLM API: {e}"}), 502
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred on the server."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
