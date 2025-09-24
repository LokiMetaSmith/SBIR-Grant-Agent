import os
import subprocess
import time
import shutil
from playwright.sync_api import sync_playwright, expect

def run_verification(playwright):
    # 1. Start the backend server without a SAM_API_KEY
    server_process = subprocess.Popen(["python", "server.py"])
    time.sleep(2)

    browser = None
    try:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:5000/")

        print("--- Testing Opportunity Search error handling ---")

        # 2. Get form elements
        keywords_input = page.locator("#searchKeywords")
        posted_from_input = page.locator("#searchPostedFrom")
        posted_to_input = page.locator("#searchPostedTo")
        search_btn = page.get_by_role("button", name="Search for Opportunities")
        results_div = page.locator("#opportunityResults")

        # 3. Fill out and submit the form
        keywords_input.fill("SBIR")
        posted_from_input.fill("2023-01-01")
        posted_to_input.fill("2023-03-31")
        search_btn.click()

        # 4. Assert that the spinner appears first
        spinner = results_div.locator(".spinner")
        expect(spinner).to_be_visible(timeout=5000)
        print("Verified spinner appeared.")

        # 5. Assert that the correct error message is displayed
        expected_error = "SAM.gov API key is not configured on the server."
        error_locator = results_div.get_by_text(f"Error: {expected_error}")

        expect(error_locator).to_be_visible(timeout=10000)
        print("Verified that the correct backend error is displayed on the frontend.")

        # 6. Take a screenshot
        page.screenshot(path="jules-scratch/verification/verification.png")
        print("Screenshot created successfully.")

    finally:
        # 7. Clean up
        if browser:
            browser.close()
        server_process.terminate()
        server_process.wait()
        print("Server process terminated.")

with sync_playwright() as playwright:
    run_verification(playwright)

print("Verification script finished.")
