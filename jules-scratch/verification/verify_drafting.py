import os
import subprocess
import time
import shutil
from playwright.sync_api import sync_playwright, expect

def run_verification(playwright):
    # 1. Set up test environment
    test_env = os.environ.copy()
    test_env["TEST_MODE"] = "true"
    test_env["LLM_1_NAME"] = "Mock Expert"
    test_env["LLM_1_ENDPOINT"] = "http://localhost:12345/v1"
    test_env["LLM_1_KEY"] = "mock-key"

    # 2. Start the backend server
    server_process = subprocess.Popen(["python", "server.py"], env=test_env)
    time.sleep(2)

    browser = None
    try:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:5000/")

        print("--- Testing Application Drafting flow ---")

        # 3. Trigger a search and click the draft button
        page.locator("#searchPostedFrom").fill("2023-01-01")
        page.locator("#searchPostedTo").fill("2023-03-31")
        page.get_by_role("button", name="Search for Opportunities").click()

        draft_btn = page.locator("#opportunityResults").get_by_role("button", name="Draft Application")
        expect(draft_btn).to_be_visible(timeout=5000)
        draft_btn.click()

        # 4. Assert that the modal appears and eventually shows the error
        modal = page.locator("#draftModal")
        expect(modal).to_be_visible()

        expected_error = "Failed to connect to the LLM API"
        error_locator = modal.get_by_text(expected_error)

        expect(error_locator).to_be_visible(timeout=10000)
        print("Verified that the correct drafting error is displayed in the modal.")

        # 5. Take a screenshot
        page.screenshot(path="jules-scratch/verification/verification.png")
        print("Screenshot created successfully.")

    finally:
        # 6. Clean up
        if browser:
            browser.close()
        server_process.terminate()
        server_process.wait()
        print("Server process terminated.")

with sync_playwright() as playwright:
    run_verification(playwright)

print("Verification script finished.")