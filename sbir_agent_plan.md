# SBIR Grant Agent - Project Plan

## Vision
To create a web-based application that helps small businesses manage their SBIR grants effectively. The application will provide tools for budget tracking, reporting, and compliance, leveraging a simulated AI agent to assist users.

## Features
The application will have the following key features:

1.  **Interactive Dashboard:**
    *   A chart to visualize the grant's budget, showing allocated vs. spent funds.
    *   A list of upcoming important deadlines (e.g., quarterly reports, final reports).

2.  **AI Reporting Assistant:**
    *   A text area where users can input their accomplishments and data for a reporting period.
    *   A button to generate a draft report based on the user's input.
    *   The AI's response will be simulated with a pre-programmed template, with the option to connect to a live LLM.

3.  **Compliance Chatbot:**
    *   A chat interface for users to ask questions about SBIR rules and regulations.
    *   The chatbot is connected to a configurable LLM API.

## Development Roadmap

### Version 1.0: Initial Prototype (Complete)
- [x] Project Setup
- [x] Feature Implementation (Simulated)
- [x] Finalization

### Version 1.1: LLM Integration (Complete)
- [x] **Compliance Chatbot:** Replaced simulated responses with a live LLM API connection.

### Future Work (Proposed)
- [ ] **Reporting Assistant:** Connect the "Generate Report Draft" feature to the LLM API.
- [ ] **Backend Server:** Create a backend (e.g., using Node.js or Python) to securely manage API keys instead of handling them in the frontend.
- [ ] **Data Persistence:** Add functionality to save and load grant data.
- [ ] **Document Store:** Implement a system for uploading, saving, and referencing documents.
- [ ] **Styling and UX:** Further refine the application's styling and user experience.
