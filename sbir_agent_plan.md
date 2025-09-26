# SBIR Grant Agent - Project Plan

## Vision
To create a web-based, AI-powered dashboard that helps small businesses manage their SBIR grants effectively. The application automates and assists with opportunity discovery, application drafting, reporting, and compliance.

## Features
The application has the following key features:

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

5.  **Automated Grant Discovery and Drafting:**
    *   A research profile to store the user's capabilities and interests.
    *   Automated daily search of `sam.gov` to find and flag matching opportunities.
    *   One-click application draft generation based on a grant and the research profile.

## Development History

### Version 1.0: Initial Prototype (Complete)
- [x] Project Setup
- [x] Feature Implementation (Simulated)

### Version 1.1: LLM Integration (Complete)
- [x] **Compliance Chatbot:** Replaced simulated responses with a live LLM API connection.
- [x] **Reporting Assistant:** Connected the "Generate Report Draft" feature to the LLM API.

### Version 1.2: Backend & Security (Complete)
- [x] **Backend Server:** Created a Python Flask backend to securely manage API keys.
- [x] **Mixture of Experts:** Allowed configuration and selection of multiple LLM providers.

### Version 1.3: Data and Documents (Complete)
- [x] **Data Persistence:** Added functionality to save and load all application data (chats, reports, etc.).
- [x] **Document Store:** Implemented a system for uploading, saving, and referencing documents.

### Version 1.4: Proactive Agent (Complete)
- [x] **Research Profile:** Created a template to store a user's capabilities and research topics.
- [x] **Automated Application Drafting:** Implemented a feature to generate initial application drafts for opportunities.
- [x] **Automated Grant Matching:** Implemented a background job to continuously search for new opportunities and flag those that match the research profile.

### Version 2.0: Finalization (Complete)
- [x] **Styling and UX:** Refined the application's styling and user experience with a tabbed interface and other improvements.
- [x] **Licensing and Documentation:** Added a GPLv3 license and updated all documentation.
- [x] **Final Review:** Completed the final review and testing of all features.