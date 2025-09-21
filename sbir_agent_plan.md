# SBIR Grant Management LLM Agent - Project Plan

## 1. Project Vision

The vision for this project is to create a fully functional, data-persistent, and AI-driven web application that automates and simplifies the entire SBIR grant lifecycle for small businesses. The tool will evolve from its current prototype stage into a comprehensive grant management assistant.

## 2. Development Phases

The development is planned in the following phases:

### Phase 1: Full LLM Integration
The initial phase focuses on replacing all simulated functionalities with live AI-driven logic using the Gemini API. This includes:
- **Compliance Agent**: A chatbot that can answer questions about SBIR/STTR grant compliance.
- **Document Generation Assistant**: An assistant to generate drafts for various documents like quarterly reports and budget justifications.
- **Key Contacts & Networking**: A feature to identify key program managers, researchers, and agency contacts.

### Phase 2: Backend and Database Implementation
This phase involves implementing a backend and database to ensure data persistence.
- **Technology**: Firebase Firestore will be used for the database.
- **Data to be Stored**: User data such as deadlines, expenses, profiles, saved grants, and chat history will be stored.
- **Authentication**: Firebase Authentication will be implemented for secure user access.

### Phase 3: Enhanced Paperwork Submission
This phase will enhance the paperwork submission feature by connecting it to a backend service.
- **Technology**: Firebase Storage will be used for file uploads.
- **Functionality**: The UI will be updated to reflect the status of the upload and provide a link to the stored file.

## 3. Core Features (as of Prototype)

The initial prototype includes the following features:
- **Dashboard**: Visualizes budget and tracks deadlines.
- **Live Grant Search**: Finds open SBIR solicitations.
- **Paperwork Submission Portal**: A simulated interface for document submission.
- **Document Generation**: Simulated creation of boilerplate documents.
- **Compliance Chatbot**: A mock chat interface.
- **Profile-Based Grant Matching**: Simulated matching of researcher profiles to grants.
- **Key Contact Identification**: Simulated identification of key contacts.
