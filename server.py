import os
import json
import re
import requests
import atexit
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
DATA_FILE = 'data.json'
UPLOAD_FOLDER = 'uploads'
EXPERTS = {}

# --- Automated Matching Job ---

def match_opportunities_job():
    """The background job that fetches and matches opportunities."""
    with app.app_context():
        print(f"[{datetime.now()}] Running automated opportunity matching job...")

        if not os.path.exists(DATA_FILE):
            print("Data file not found. Skipping job.")
            return
        with open(DATA_FILE, 'r') as f:
            app_data = json.load(f)

        profile = app_data.get("researchProfile")
        if not profile or not profile.get("capabilities") or not profile.get("topics"):
            print("Research profile is empty. Skipping job.")
            return

        sam_api_key = os.getenv("SAM_API_KEY")
        if not sam_api_key:
            print("SAM.gov API key not configured. Skipping job.")
            return

        postedTo = datetime.now().strftime('%m/%d/%Y')
        postedFrom = (datetime.now() - timedelta(days=7)).strftime('%m/%d/%Y')

        search_keywords = profile.get("keywords", "Grant")
        params = {"api_key": sam_api_key, "limit": 100, "postedFrom": postedFrom, "postedTo": postedTo, "title": search_keywords}
        try:
            response = requests.get("https://api.sam.gov/opportunities/v2/search", params=params, timeout=30)
            response.raise_for_status()
            opportunities = response.json().get("opportunitiesData", [])
            print(f"Found {len(opportunities)} new opportunities to analyze.")
        except requests.exceptions.RequestException as e:
            print(f"Error calling SAM.gov API in background job: {e}")
            return

        if not EXPERTS:
            print("No LLM experts configured for matching. Skipping analysis.")
            return

        expert_name = list(EXPERTS.keys())[0]
        expert = EXPERTS[expert_name]

        matched_opportunities = app_data.get("matchedOpportunities", [])
        existing_notice_ids = {opp['opportunity']['noticeId'] for opp in matched_opportunities}

        for opp in opportunities:
            if opp.get('noticeId') in existing_notice_ids:
                continue

            prompt = f"""
            Analyze the following grant opportunity and determine if it is a good match for the given research profile.

            **Research Profile:**
            - Capabilities: {profile['capabilities']}
            - Topics: {profile['topics']}

            **Grant Opportunity:**
            - Title: {opp.get('title', 'N/A')}
            - Description: {opp.get('description', 'N/A')}

            **Instructions:**
            Respond with a JSON object containing ONLY two keys: "is_match" (boolean) and "justification" (a brief, one-sentence explanation).
            """
            messages = [{"role": "system", "content": prompt}]
            payload = {"model": expert["model_name"], "messages": messages}
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {expert["api_key"]}'}

            try:
                llm_response = requests.post(expert["endpoint"], headers=headers, json=payload, timeout=90)
                llm_response.raise_for_status()
                analysis_text = llm_response.json()['choices'][0]['message']['content']
                analysis_json = json.loads(analysis_text.strip().replace("```json", "").replace("```", ""))

                if analysis_json.get("is_match") == True:
                    print(f"Found a match: {opp.get('title')}")
                    matched_opportunities.append({
                        "opportunity": opp,
                        "match_analysis": analysis_json,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Error analyzing opportunity {opp.get('noticeId')} with LLM: {e}")
                continue

        app_data["matchedOpportunities"] = matched_opportunities
        with open(DATA_FILE, 'w') as f:
            json.dump(app_data, f, indent=4)
        print("Automated matching job finished.")


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
            model_name = os.getenv(f"LLM_{index}_MODEL_NAME", name)
            if name and endpoint and api_key:
                experts_config[name] = {"endpoint": endpoint, "api_key": api_key, "model_name": model_name}
    EXPERTS = experts_config
    if not EXPERTS:
        print("Warning: No LLM experts configured.")
    else:
        print(f"Loaded experts: {list(EXPERTS.keys())}")

# --- Test-only Endpoints ---
@app.route('/api/test_match_job', methods=['POST'])
def trigger_match_job():
    """Triggers the matching job on demand for testing."""
    match_opportunities_job()
    return jsonify({"success": True, "message": "Matching job triggered."})

@app.route('/api/mock_llm', methods=['POST'])
def mock_llm_responder():
    """A mock LLM endpoint for testing the matching job."""
    return jsonify({
        "choices": [{
            "message": {
                "content": '{\n  "is_match": true,\n  "justification": "This is a perfect match based on the profile."\n}'
            }
        }]
    })

# --- API Endpoints ---

@app.route('/')
def index():
    return send_from_directory('.', 'sbir_agent.html')

@app.route('/api/experts', methods=['GET'])
def get_experts():
    return jsonify(list(EXPERTS.keys()))

@app.route('/api/organization_details', methods=['POST'])
def organization_details():
    if os.getenv("TEST_MODE") == "true":
        return jsonify({
            "fhorgname": "Test Agency",
            "fhorgtype": "Department/Ind. Agency",
            "status": "ACTIVE",
            "description": "This is a mock organization for testing purposes.",
            "links": [{"rel": "self", "href": "http://example.com"}]
        })

    sam_api_key = os.getenv("SAM_API_KEY")
    if not sam_api_key:
        return jsonify({"error": "SAM.gov API key is not configured on the server."}), 500

    data = request.get_json()
    org_name = data.get('keywords', '')

    if not org_name:
         return jsonify({"error": "Organization name (keywords) is required."}), 400

    params = {
        "api_key": sam_api_key,
        "fhorgname": org_name,
        "limit": 1
    }

    try:
        response = requests.get("https://api.sam.gov/prod/federalorganizations/v1/orgs", params=params, timeout=30)
        response.raise_for_status()
        org_list = response.json().get("orglist", [])
        if org_list:
             return jsonify(org_list[0])
        else:
             return jsonify({"error": "Organization not found."}), 404

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to the SAM.gov Federal Hierarchy API: {e}"}), 502
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/api/search_opportunities', methods=['POST'])
def search_opportunities():
    if os.getenv("TEST_MODE") == "true":
        return jsonify([{"title": "Test Grant Opportunity", "fullParentPathName": "Test Agency", "solicitationNumber": "TEST-123", "postedDate": "2025-09-25", "description": "This is a test opportunity for drafting.", "uiLink": "http://example.com"}])
    sam_api_key = os.getenv("SAM_API_KEY")
    if not sam_api_key:
        return jsonify({"error": "SAM.gov API key is not configured on the server."}), 500
    data = request.get_json()
    params = {
        "api_key": sam_api_key, "limit": 50, "postedFrom": data.get('postedFrom'), "postedTo": data.get('postedTo'), "title": data.get('keywords', '')
    }
    if not params["postedFrom"] or not params["postedTo"]:
        return jsonify({"error": "A date range is required."}), 400
    try:
        response = requests.get("https://api.sam.gov/opportunities/v2/search", params=params, timeout=30)
        response.raise_for_status()
        return jsonify(response.json().get("opportunitiesData", []))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to the SAM.gov API: {e}"}), 502
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/api/draft_application', methods=['POST'])
def draft_application():
    data = request.get_json()
    if not data or 'opportunity' not in data or 'profile' not in data or 'expert' not in data:
        return jsonify({"error": "Invalid request body."}), 400
    expert = EXPERTS.get(data['expert'])
    if not expert:
        return jsonify({"error": f"Expert '{data['expert']}' not found."}), 404
    prompt = f"You are a professional grant writer... Capabilities: {data['profile'].get('capabilities', 'N/A')}... Opportunity: {data['opportunity'].get('title', 'N/A')}..."
    messages = [{"role": "system", "content": prompt}]
    payload = {"model": expert["model_name"], "messages": messages}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {expert["api_key"]}'}
    try:
        response = requests.post(expert["endpoint"], headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        return jsonify({"draft": response.json()['choices'][0]['message']['content']})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to the LLM API: {e}"}), 502
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({"success": True, "filename": filename, "path": f"/{UPLOAD_FOLDER}/{filename}"}), 201

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/data', methods=['GET'])
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"budget": {}, "deadlines": [], "reportText": "", "chatHistory": [], "documents": [], "researchProfile": {}, "matchedOpportunities": []})
    except Exception as e:
        return jsonify({"error": "Could not load data."}), 500

@app.route('/api/data', methods=['POST'])
def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(request.get_json(), f, indent=4)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": "Could not save data."}), 500

@app.route('/api/chat', methods=['POST'])
def chat_handler():
    data = request.get_json()
    if not data or 'messages' not in data or 'model' not in data:
        return jsonify({"error": "Invalid request body."}), 400
    expert = EXPERTS.get(data['model'])
    if not expert:
        return jsonify({"error": f"Expert '{data['model']}' not found."}), 404
    payload = {"model": expert["model_name"], "messages": data["messages"]}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {expert["api_key"]}'}
    try:
        response = requests.post(expert["endpoint"], headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to LLM API: {e}"}), 502
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    load_experts_from_env()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=match_opportunities_job, trigger="interval", days=1, next_run_time=datetime.now() + timedelta(seconds=5))
    scheduler.start()
    print("Scheduler started. Will run job in 5 seconds for testing, then daily.")
    atexit.register(lambda: scheduler.shutdown())

    app.run(debug=True, port=5000, use_reloader=False)