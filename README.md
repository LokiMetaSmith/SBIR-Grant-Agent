# SBIR Grant Agent

This project is a web-based, AI-powered dashboard designed to help small businesses manage their SBIR (Small Business Innovation Research) government grants. It automates and assists with opportunity discovery, application drafting, reporting, and compliance.

## Features
*   **Automated Grant Matching:** A background agent runs daily to search for new grant opportunities on `sam.gov`. It uses an LLM to compare opportunities against your company's research profile and flags the most relevant ones for your review.
*   **Interactive Dashboard:** Visualize your grant's budget, keep track of important deadlines, and see automatically flagged opportunities in a clean, modern interface.
*   **Automated Application Drafting:** For any grant opportunity, click "Draft Application" to have an LLM generate a high-quality initial draft based on the opportunity's requirements and your saved research profile.
*   **Mixture of Experts (MoE) LLM Integration:** Configure and connect multiple LLMs (e.g., from OpenAI, Anthropic, Cohere). You can select which "expert" model to use for different tasks like drafting applications or answering compliance questions.
*   **AI Reporting Assistant:** Generate drafts for your quarterly and final reports by providing key data points and accomplishments.
*   **Compliance Chatbot:** Get real-time answers to your questions about SBIR rules and regulations.
*   **Document Store:** Upload and manage important grant-related documents directly within the application.
*   **Data Persistence:** Your application state, including uploaded documents, chat history, and research profile, is automatically saved to the server.

## Technical Details
*   **Frontend:** The application is a single-page application built with HTML, Tailwind CSS for styling, and vanilla JavaScript for interactivity. Charts are rendered using Chart.js.
*   **Backend:** A Python Flask server that:
    *   Acts as a secure proxy to handle API calls to LLMs, keeping API keys off the frontend.
    *   Serves the main application and uploaded documents.
    *   Handles file uploads and data persistence (`data.json`).
    *   Runs a scheduled background job (using APScheduler) for automated grant matching.

## Project Structure
*   `sbir_agent.html`: The main file containing the HTML structure, styling, and JavaScript logic for the frontend.
*   `server.py`: The Python Flask backend server.
*   `requirements.txt`: Python dependencies for the backend.
*   `.env.example`: An example file showing the required environment variables.
*   `LICENSE`: The GPLv3 License file.
*   `ToDo.md`: A list of potential future improvements and features.
*   `sbir_agent_plan.md`: The original high-level project plan.
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
- `LLM_[INDEX]_MODEL_NAME`: (Optional) The specific model name the API expects (e.g., "gpt-4-turbo").

You can add as many experts as you like by incrementing the index (e.g., `LLM_1_...`, `LLM_2_...`, etc.). The names you provide will appear in the dropdown menus in the application.

You will also need to provide a `SAM_API_KEY` to enable the Grant Opportunity Search and Automated Matching features. You can obtain a key by registering on `sam.gov`.

**b. Create a Virtual Environment and Install Dependencies:**
It is highly recommended to use a Python virtual environment.

```bash
# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt
```

### 2. Running the Application

**a. Start the Backend Server:**
With your virtual environment activated, run the following command in your terminal:
```bash
python3 server.py
```
The server will start on `http://127.0.0.1:5000`.

**b. Open the Frontend:**
Navigate to `http://127.0.0.1:5000/sbir_agent.html` in your web browser. The application is now ready to use.