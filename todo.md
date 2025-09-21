# SBIR Grant Management Agent - To-Do List

This file tracks the development tasks for the project.

## Development Roadmap

- [ ] **Task 1: Full LLM Integration**
  - [ ] **Compliance Agent**: Connect the chat interface to the Gemini API.
  - [ ] **Document Generation Assistant**: Use the Gemini API to generate document drafts.
  - [ ] **Key Contacts & Networking**: Implement a Gemini API call to identify key contacts.

- [ ] **Task 2: Implement Backend & Database for Persistence**
  - [ ] **Backend**: Integrate Firebase Firestore for the database.
  - [ ] **Data to Store**:
    - [ ] Tracked deadlines.
    - [ ] Logged expenses and budget status.
    - [ ] Researcher profile information.
    - [ ] Saved grants of interest.
    - [ ] Chat history.
  - [ ] **Authentication**: Implement Firebase Authentication to allow users to sign in and save their data securely.

- [ ] **Task 3: Enhance the Paperwork Submission Feature**
  - [ ] Connect the paperwork submission feature to a backend service (e.g., Firebase Storage).
  - [ ] Update the UI to reflect the successful upload and provide a link to the stored file.
