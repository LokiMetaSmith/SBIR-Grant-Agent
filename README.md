# SBIR Grant Agent

This project is a web-based application designed to help small businesses manage their SBIR (Small Business Innovation Research) government grants. It features an AI-powered agent to assist with reporting, compliance, and overall project management.

## Features
*   **Interactive Dashboard:** Visualize your grant's budget and keep track of important deadlines.
*   **AI Reporting Assistant:** Generate drafts for your quarterly and final reports by providing key data points. This feature is powered by a configurable LLM.
*   **Compliance Chatbot:** Get answers to your questions about SBIR rules and regulations in real-time, powered by a configurable LLM.

## Technical Details
*   **Frontend:** The application is a single-page application built with HTML, Tailwind CSS for styling, and vanilla JavaScript for interactivity. Charts are rendered using Chart.js.
*   **Backend:** A simple Python Flask server acts as a secure proxy to handle API calls to the Language Model (LLM). This keeps API keys off the frontend.

## Project Structure
*   `sbir_agent.html`: The main file containing the HTML structure, styling, and JavaScript logic for the frontend application.
*   `server.py`: The Python Flask backend server that forwards requests to the LLM API.
*   `requirements.txt`: The Python dependencies for the backend server.
*   `.env.example`: An example file showing the required environment variables for the server.
*   `sbir_agent_plan.md`: The project plan outlining the vision, features, and development roadmap.
*   `README.md`: This file.

## How to Run

### 1. Backend Setup
Before running the application, you need to set up the backend server.

**a. Configure Environment Variables:**
Create a `.env` file in the root of the project by copying the `.env.example` file. This file allows you to configure multiple LLM "experts".

The backend will load any environment variables that follow this pattern:
- `LLM_[INDEX]_NAME`: The display name for the expert (e.g., "OpenAI GPT-4").
- `LLM_[INDEX]_ENDPOINT`: The full API endpoint URL.
- `LLM_[INDEX]_KEY`: The secret API key for that service.
- `LLM_[INDEX]_MODEL_NAME`: (Optional) The specific model name the API expects (e.g., "gpt-4-turbo"). If not provided, it defaults to the `NAME`.

You can add as many experts as you like by incrementing the index (e.g., `LLM_1_...`, `LLM_2_...`, etc.). The names you provide will appear in the dropdown menus in the application.

**b. Install Dependencies:**
Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 2. Running the Application

**a. Start the Backend Server:**
Run the following command in your terminal:
```bash
python server.py
```
The server will start on `http://127.0.0.1:5000`.

**b. Open the Frontend:**
Open the `sbir_agent.html` file in your web browser. The application will now be able to communicate with your backend, which will securely connect to the LLM.
