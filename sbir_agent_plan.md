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
    *   This feature is connected to a live LLM via a secure backend.

3.  **Compliance Chatbot:**
    *   A chat interface for users to ask questions about SBIR rules and regulations.
    *   This feature is connected to a live LLM via a secure backend.

4.  **Document Store:**
    *   An interface for uploading, storing, and referencing grant-related documents.

## Development Roadmap

### Version 1.0: Initial Prototype (Complete)
- [x] Project Setup
- [x] Feature Implementation (Simulated)
- [x] Finalization

### Version 1.1: LLM Integration (Complete)
- [x] **Compliance Chatbot:** Replaced simulated responses with a live LLM API connection.
- [x] **Reporting Assistant:** Connected the "Generate Report Draft" feature to the LLM API.

### Version 1.2: Backend & Security (Complete)
- [x] **Backend Server:** Created a backend to securely manage API keys.

### Version 1.3: Data Persistence (Complete)
- [x] **Data Persistence:** Added functionality to save and load grant data.

### Version 1.4: Document Store (Complete)
- [x] **Document Store:** Implemented a system for uploading, saving, and referencing documents.

### Version 1.5: UI/UX Polish (Complete)
- [x] **Styling and UX:** Refined the application's styling and user experience.

### Version 1.6: Mixture of Experts (Complete)
- [x] **Mixture of Experts:** Allowed configuration and selection of multiple LLM providers.

### Version 1.7: Research Profile (Complete)
- [x] **Research Profile:** Created a template to store a user's capabilities and research topics.

### Version 1.8: Automated Agent Features (In Progress)
- [ ] **Automated Application Drafting:** Generate initial application drafts for opportunities.
- [ ] **Automated Grant Matching:** Continuously search for new opportunities and flag those that match the research profile.
- [ ] **Styling and UX:** Further refine the application's styling and user experience.
