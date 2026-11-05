import re
from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Mock data API
    page.route("**/api/data", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"budget": {"spent": 50000, "remaining": 50000}, "deadlines": [{"name": "Q1 Report", "date": "2024-03-31"}], "reportText": "", "chatHistory": [], "documents": [], "researchProfile": {"keywords": "Health", "capabilities": "AI, ML", "topics": "Mental Health"}, "matchedOpportunities": []}'
    ) if route.request.method == "GET" else route.fulfill(status=200, content_type="application/json", body='{"success": true}'))

    # Mock experts API
    page.route("**/api/experts", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='["Mock Expert 1", "Mock Expert 2"]'
    ))

    # Mock search opportunities API
    page.route("**/api/search_opportunities", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='[{"title": "Test Opportunity 1", "fullParentPathName": "Department of Health", "solicitationNumber": "SOL-123", "postedDate": "2024-01-01", "uiLink": "http://example.com"}]'
    ))

    # Mock chat API
    page.route("**/api/chat", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"choices": [{"message": {"content": "This is a generated report draft."}}]}'
    ))

    # Mock upload API
    page.route("**/api/upload", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"success": true, "filename": "test.txt", "path": "/uploads/test.txt"}'
    ))

    page.goto("http://127.0.0.1:5000/sbir_agent.html")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Non-Profit Grant Agent"))

    # 1. Verify the tabbed interface
    search_tab = page.locator("#tab-search")
    profile_tab = page.locator("#tab-profile")
    psc_tab = page.locator("#tab-psc")
    search_content = page.locator("#content-search")
    profile_content = page.locator("#content-profile")
    psc_content = page.locator("#content-psc")

    # Initially, Search tab should be active and its content visible
    expect(search_tab).to_have_class(re.compile("active"))
    expect(search_content).to_be_visible()
    expect(profile_content).to_be_hidden()
    expect(psc_content).to_be_hidden()

    # 2. Click on the PSC tab and Verify PSC Search
    psc_tab.click()
    expect(psc_tab).to_have_class(re.compile("active"))
    expect(search_content).to_be_hidden()
    expect(profile_content).to_be_hidden()
    expect(psc_content).to_be_visible()

    # Mock PSC search
    page.route("**/api/psc", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='[{"pscCode": "R425", "pscName": "Engineering and Technical Services", "description": "Engineering services."}]'
    ))

    page.locator("#pscKeywords").fill("Engineering")
    page.locator("button:has-text('Search PSC')").click()

    # Wait for PSC results
    psc_results = page.locator("#pscResults")
    expect(psc_results).to_contain_text("R425")
    expect(psc_results).to_contain_text("Engineering and Technical Services")

    # 3. Click on the Profile tab and Verify Saving Profile
    profile_tab.click()
    expect(profile_tab).to_have_class(re.compile("active"))
    expect(search_content).to_be_hidden()
    expect(profile_content).to_be_visible()
    expect(psc_content).to_be_hidden()

    capabilities_input = page.locator("#capabilities")
    expect(capabilities_input).to_have_value("AI, ML")

    capabilities_input.fill("AI, ML, Data Science")
    page.locator("#saveProfileBtn").click()
    expect(page.locator("#profileSaveStatus")).to_have_text("Saved!")

    # 4. Go back to Search tab and Verify Search
    search_tab.click()
    page.locator("#searchKeywords").fill("Healthcare")
    page.locator("#searchPostedFrom").fill("2024-01-01")
    page.locator("#searchPostedTo").fill("2024-12-31")
    page.locator("button[type='submit']", has_text="Search for Opportunities").click()

    results = page.locator("#opportunityResults")
    expect(results).to_contain_text("Test Opportunity 1")
    expect(results).to_contain_text("Department of Health")

    # 5. Verify AI Reporting Assistant
    report_input = page.locator("#reportInput")
    report_input.fill("We completed phase 1 of the trial.")
    page.locator("#generateReportBtn").click()

    report_output = page.locator("#reportOutput")
    expect(report_output).to_be_visible()
    expect(report_output).to_contain_text("This is a generated report draft.")

    # 6. Verify Document Upload flow
    file_input = page.locator("#fileInput")
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(b"test file content")
        tmp_name = tmp.name

    file_input.set_input_files(tmp_name)
    page.locator("button:has-text('Upload Document')").click()

    # Verify the document appears in the list
    expect(page.locator("#documentList")).to_contain_text("test.txt")
    os.remove(tmp_name)

    # 7. Verify the footer is present
    footer = page.locator("footer")
    expect(footer).to_be_visible()
    expect(footer).to_contain_text("Grant Management Dashboard - © 2024. Licensed under GPLv3.")

    # 8. Take a screenshot of the final state
    page.screenshot(path="final_ux_screenshot.png")

    # 9. Close context and browser
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
