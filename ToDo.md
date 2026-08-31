# Project ToDo and Research Plan

This document outlines the future work and research plan for the Non-Profit Grant Agent application.

---

## 1. High-Level Implementation Plan for `sam.gov` APIs

Based on the research of available APIs, the following features can be implemented to enhance the application.

### Feature 1: Grant Opportunity Search (Completed)
- **Description:** Allow users to search for grant opportunities directly from the application.
- **API Used:** `SAM.gov Get Opportunities Public API`
- **Implementation:**
    - [x] Add `SAM_API_KEY` to `.env` configuration.
    - [x] Create a backend endpoint (`/api/search_opportunities`) to securely query the API.
    - [x] Create a frontend UI with search inputs and a results display area.
    - [x] Verify and finalize this feature.

### Feature 2: Organization Details Lookup (Completed)
- **Description:** In the opportunity search results, provide a "Details" button for each organization (awarding agency, etc.) that, when clicked, fetches and displays more information about that entity.
- **APIs Used:** `SAM.gov Entity Management API` and `SAM.gov Federal Hierarchy Public API`.
- **Implementation:**
    - [x] Add a new backend endpoint (e.g., `/api/organization_details`).
    - [x] This endpoint will take an organization identifier and query the relevant `sam.gov` API.
    - [x] Update the frontend to include the "Details" button and a modal or panel to display the fetched information.

### Feature 3: Product Service Code (PSC) Explorer (Completed)
- **Description:** Add a tool that allows users to search for PSC codes by keyword or to look up the meaning of a specific PSC code. This helps users find relevant opportunities.
- **API Used:** `SAM.gov Product Service Codes (PSC) API`.
- **Implementation:**
    - [x] Add a new backend endpoint (e.g., `/api/psc`).
    - [x] Add a new UI section for the PSC Explorer tool.
    - [x] Verified with mock data and Playwright test.

---

## 2. Future Feature Roadmap (Based on Research)

The following features have been identified as valuable additions to standard non-profit grant management software and should be considered for future development.

### Feature 4: Workflow Automation & Deadline Management
- **Description:** Implement automated reminders for upcoming deadlines (reporting, application submission, renewal).
- **Activities:**
    - Integrate an email notification system (e.g., SendGrid or SMTP).
    - Enhance the scheduler to check for deadlines and send alerts.
    - Create a calendar view in the frontend to visualize deadlines.

### Feature 5: Comprehensive Budget Management
- **Description:** Expand the "Budget Overview" to support detailed expense tracking, budget vs. actuals reporting, and multi-grant budget management.
- **Activities:**
    - Create a data model for line-item expenses.
    - Update the UI to allow adding/editing expenses.
    - Generate detailed financial reports (leveraging the Reporting Assistant).

### Feature 6: Collaboration Tools
- **Description:** Enable multiple users to collaborate on grant applications and reports.
- **Activities:**
    - Implement user authentication and role-based access control.
    - Add real-time or near real-time notes/comments on drafts.
    - Create a shared "Team Profile" vs individual user profiles.

### Feature 7: Integrations
- **Description:** Connect with external tools used by non-profits.
- **Activities:**
    - Investigate integrations with common CRMs (e.g., Salesforce, HubSpot) for donor/funder management.
    - Investigate integrations with accounting software (e.g., QuickBooks, Xero).

---

## 3. Research Plan for Project Architecture

This section outlines a plan to evaluate and potentially refactor the project's architecture to support future growth and maintainability.

### Phase 1: Assessment (1-2 hours)
- **Goal:** Understand the current state and identify pain points.
- **Activities:**
    - Review the single `sbir_agent.html` file and measure its line count. A large single file can be difficult to maintain.
    - Review the single `server.py` file. Assess its complexity and separation of concerns.
    - Analyze the "full-stack" verification process. Is it becoming slow or brittle?

### Phase 2: Frontend Refactoring Evaluation (2-3 hours)
- **Goal:** Evaluate moving from vanilla JavaScript to a modern frontend framework.
- **Research Questions:**
    - Would a framework like React, Vue, or Svelte simplify state management?
    - How would a component-based architecture improve code organization and reuse?
    - What is the effort required to migrate the existing UI into components?
- **Outcome:** A recommendation on whether to adopt a frontend framework, and which one would be most suitable.

### Phase 3: Backend & Deployment Evaluation (2-3 hours)
- **Goal:** Evaluate improvements to the backend and consider deployment strategies.
- **Research Questions:**
    - Should the single `server.py` be broken into multiple files (e.g., using Flask Blueprints) for better organization?
    - Is the `data.json` file sufficient for data persistence, or should we consider a more robust solution like SQLite?
    - What are the simplest and most effective ways to deploy this full-stack application (e.g., using Docker, a PaaS like Heroku, etc.)?
- **Outcome:** A recommendation on backend structure and a simple deployment strategy.

### Phase 4: Final Report
- **Goal:** Synthesize all findings into a final architecture proposal.
- **Activities:**
    - Create a document outlining the recommended architecture, including technology choices, project structure, and a proposed roadmap for the refactoring effort.

---

## 4. Testing, Benchmarks, and Experiments Refactoring

During code review, a few areas of 'lazy code' were identified in the project's testing, benchmarking, and experimental setup that do not perform the function their name suggests. These areas need improvement:

### Area 1: `verify_final_ux.py` (End-to-End Testing)
- **Issue:** The script is named `verify_final_ux.py` but is a very 'lazy' test. It only verifies that a few tabs can be clicked and checks the text of the footer. Furthermore, it expects the outdated title 'SBIR Grant Agent' instead of the current 'Non-Profit Grant Agent', causing it to fail completely. It does not actually verify the 'final UX' of the application (e.g., searching, generating reports, saving profiles, or uploading documents).
- **Improvement:** Refactor `verify_final_ux.py` to actually test the core user flows of the application (e.g., successfully submitting a search form, interacting with the AI Reporting Assistant, saving a research profile, and verifying the expected DOM updates). Update all outdated text assertions to match the current application state.

### Area 2: Hardcoded Test Routes and `TEST_MODE` in `server.py`
- **Issue:** The backend `server.py` contains production routes like `/api/test_match_job` and `/api/mock_llm` explicitly designated as 'Test-only Endpoints', and it litters production logic with `if os.getenv("TEST_MODE") == "true":` to return mock data (e.g., in `/api/organization_details` and `/api/search_opportunities`). This is a lazy testing/experimentation approach that mixes test stubs into production code.
- **Improvement:** Remove `TEST_MODE` blocks and 'Test-only Endpoints' from the main `server.py`. Introduce a proper testing framework (like `pytest`) and use dedicated mocking libraries (like `unittest.mock` or `responses`) to intercept API calls during testing. If experimental test endpoints are needed for local development, isolate them in a separate test server file or use Flask Blueprints loaded conditionally.
