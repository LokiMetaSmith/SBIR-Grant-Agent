# SBIR Grant Management Agent Project - Agent Guidelines

This document provides guidelines for the AI agent working on this project.

## Coding Guidelines & Constraints

- **Maintain Single-File Frontend**: For now, all frontend changes (HTML, CSS, JS) should be made within `sbir_agent.html`.
- **Asynchronous Operations**: All API calls and database interactions must be handled asynchronously (`async`/`await`) to keep the UI responsive.
- **Error Handling**: Implement robust error handling for API calls and display user-friendly error messages in the UI (e.g., "Failed to fetch grants, please try again.").
- **API Keys**: Ensure that no API keys are hardcoded directly in the JavaScript. Use a placeholder variable (e.g., `const apiKey = "";`).
- **Frameworks**: The project uses vanilla JavaScript, HTML5, and Tailwind CSS (via CDN). Chart.js is used for charts (via CDN). The backend will be Firebase/Firestore.
- **LLM/AI**: The project uses the Gemini API.

## Development Roadmap

The primary goal is to replace all simulated functionalities with live backend and AI-driven logic. The development is divided into the following tasks:

### Task 1: Full LLM Integration
- **Compliance Agent**: Connect the chat interface to the Gemini API.
- **Document Generation Assistant**: Use the Gemini API to generate document drafts.
- **Key Contacts & Networking**: Implement a Gemini API call to identify key contacts.

### Task 2: Implement Backend & Database for Persistence
- **Backend**: Integrate Firebase Firestore for the database.
- **Data to Store**:
    - Tracked deadlines.
    - Logged expenses and budget status.
    - Researcher profile information.
    - Saved grants of interest.
    - Chat history.
- **Authentication**: Implement Firebase Authentication.

### Task 3: Enhance the Paperwork Submission Feature
- Connect the submission feature to a backend service (e.g., Firebase Storage).

## Initial Task

The first specific task is to implement **Task 1**, starting with the **"Key Contacts & Networking"** feature. Replace the current `setTimeout` simulation with a live Gemini API call.
