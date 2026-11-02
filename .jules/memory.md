## Archived: 2026-11-02

* The project 'Grant Management Dashboard' (formerly 'Non-Profit Grant Agent' and 'SBIR Grant Agent') consists of a Python Flask backend (`server.py`) and a single-file HTML frontend (`sbir_agent.html`) using Tailwind CSS and Chart.js.
* Backend endpoints are tested using `pytest` in `test_server.py`, utilizing `unittest.mock` to mock external SAM.gov and LLM API calls. This replaces earlier hardcoded test endpoints and `TEST_MODE` blocks.
* UI/UX Preference: Prevent dashboard bloat by integrating new tools, views, and data points into existing UI flows and structures rather than creating new top-level tabs.
* The application supports manual opportunity entry to track and draft proposals for non-SAM.gov grants, such as private foundation or NSF grants.
* Project tasks, feature requests, and implementation plans are tracked in `ToDo.md`.
* The application acts as an OpenClaw-compatible agent, exposing an ATProto verification identity via a `/.well-known/atproto-did` endpoint.
* The AI Reporting Assistant captures structured quantitative metrics (Progress Status, Quality, Time Spent, Milestone Percentages) persisted in the `reportMetrics` state. Updating milestone completion percentages automatically synchronizes with the global `otaMilestones` data.
* The agent's ATProto Decentralized Identifier (DID) is configured using the `ATPROTO_DID` environment variable.
* The automated grant matching job uses user-defined keywords from the research profile to query the SAM.gov API, replacing hardcoded search terms.
* The backend relies on dependencies listed in `requirements.txt`: Flask, requests, python-dotenv, and APScheduler.
* Frontend UI changes and E2E UX are verified using Playwright scripts such as `verify_final_ux.py`.
* The application supports multiple organization types (e.g., Non-Profit, For-Profit, Academic Institution, NGO) and automatically tailors AI grant proposal drafts according to the selected organization type.
* The AI Budget Planner supports MTDC (Modified Total Direct Cost) and TDC overhead calculation toggles. MTDC strictly enforces federal exclusions by automatically deducting Equipment, Participant Support, and any Subaward amounts over $25,000 from the base before applying the F&A (overhead) rate.
* The application supports drafting 'Mini-study (OSDR Praxis)' proposals using specific OSDR fields (Data Review Type, Mini-study Context) stored in the Research Profile.
* Persistent storage in the containerized environment is configured via the `DATA_FILE` and `UPLOAD_FOLDER` environment variables, defaulting to a volume-mountable `/app/data` directory.
* To run the backend server, execute `python3 server.py`. To run the user experience tests, execute `python3 verify_final_ux.py`. To run backend unit tests, execute `python3 -m pytest test_server.py`.
* The application includes an AI Budget Planner with sub-tabs for Summary, Direct Labor, Equipment, Travel, Other Costs, Participant Support, and Subawards. It parses natural language to auto-populate budget tables, persisting data in `laborBudgets`, `equipmentBudgets`, `otherCostsBudgets`, `participantBudgets`, `subawardBudgets`, `travelBudgets`, and `projectDetails`. It utilizes a mocked GSA Per Diem API (`/api/gsa_perdiem`) for domestic travel cost estimations.
* To set up the development environment, install dependencies using `pip install -r requirements.txt`.
* The application integrates with SAM.gov APIs (Get Opportunities, Federal Hierarchy, and Product Service Codes) and requires a `SAM_API_KEY` in the environment.
* The application supports Other Transactions Agreement (OTA) proposal drafting and milestone-driven execution tracking alongside standard federal grants.
* Directive: Always start tasks in a deep planning mode. Prioritize understanding requirements by asking clarifying questions using the `request_user_input` and `message_user` tools before executing `set_plan`.
* The application is containerized and deployed as a plugin/module on an external cluster using a standardized `manifest.json` schema and a standard Dockerfile.
