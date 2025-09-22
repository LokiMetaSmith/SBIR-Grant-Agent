import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
DATA_FILE = 'data.json'

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
                "chatHistory": []
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

@app.route('/api/chat', methods=['POST'])
def chat_handler():
    # 1. Get data from the frontend request
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({"error": "Invalid request body. 'messages' key is required."}), 400

    # 2. Get LLM API details from environment variables
    llm_api_endpoint = os.getenv("LLM_API_ENDPOINT")
    llm_api_key = os.getenv("LLM_API_KEY")

    if not llm_api_endpoint or not llm_api_key:
        return jsonify({"error": "LLM API endpoint or key is not configured on the server."}), 500

    # 3. Prepare the request for the external LLM API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {llm_api_key}'
    }

    # Pass through the model and messages from the original request
    payload = {
        "model": data.get("model", "gpt-3.5-turbo"), # Default model if not provided
        "messages": data["messages"]
    }

    # 4. Forward the request and handle potential errors
    try:
        response = requests.post(llm_api_endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Return the external API's response to the frontend
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        print(f"Error calling LLM API: {e}")
        return jsonify({"error": f"Failed to connect to the LLM API: {e}"}), 502 # Bad Gateway
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred on the server."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
