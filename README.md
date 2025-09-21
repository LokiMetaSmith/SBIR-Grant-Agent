# SBIR Grant Management LLM Agent

## 1. About the Project

The SBIR Grant Management LLM Agent is an AI-driven web application designed to automate and simplify the entire SBIR grant lifecycle for small businesses. This tool helps researchers and entrepreneurs manage their grant applications, from finding opportunities to submitting paperwork and ensuring compliance.

## 2. Core Features

The application includes the following features:

- **Dashboard**: Visualize your budget with dynamic charts and keep track of important deadlines.
- **Live Grant Search**: Find open SBIR solicitations using an AI-powered search that leverages the latest information from the web.
- **Paperwork Submission Portal**: Upload and manage your grant-related documents.
- **Document Generation**: Automatically generate boilerplate for common documents like quarterly reports and budget justifications.
- **Compliance Chatbot**: Get answers to your compliance questions from an AI expert trained on official grant regulations.
- **Profile-Based Grant Matching**: Discover grant opportunities that are a perfect match for your research profile.
- **Key Contact Identification**: Identify key program managers, researchers, and agency contacts in your field.

## 3. Technical Stack

- **Frontend**: Vanilla JavaScript, HTML5
- **Styling**: Tailwind CSS (loaded via CDN)
- **Charts**: Chart.js (loaded via CDN)
- **LLM/AI**: Gemini API
- **Backend**: Firebase (Firestore for database, Storage for file uploads, and Authentication for user management)

## 4. Setup and Installation

To run this project, you will need a modern web browser and an internet connection. The application is designed to be a single-file web app, so you can simply open the `sbir_agent.html` file in your browser.

**Note**: To use the AI-powered features, you will need to provide your own Gemini API key. The application will prompt you for the key when needed.
