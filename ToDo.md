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

### Feature 3: Product Service Code (PSC) Explorer
- **Description:** Add a tool that allows users to search for PSC codes by keyword or to look up the meaning of a specific PSC code. This helps users find relevant opportunities.
- **API Used:** `SAM.gov Product Service Codes (PSC) API`.
- **Implementation:**
    - Add a new backend endpoint (e.g., `/api/psc`).
    - Add a new UI section for the PSC Explorer tool.

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