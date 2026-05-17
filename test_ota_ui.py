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
        body='{"budget": {"spent": 50000, "remaining": 50000}, "deadlines": [], "otaMilestones": [], "reportText": "", "chatHistory": [], "documents": [], "researchProfile": {}, "matchedOpportunities": []}'
    ) if route.request.method == "GET" else route.fulfill(status=200, content_type="application/json", body='{"success": true}'))

    # Mock experts API
    page.route("**/api/experts", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='["Mock Expert 1"]'
    ))

    # Mock search opportunities API
    page.route("**/api/search_opportunities", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='[{"title": "Test Opportunity 1", "fullParentPathName": "Department of Health", "solicitationNumber": "SOL-123", "postedDate": "2024-01-01", "uiLink": "http://example.com"}]'
    ))

    # Mock draft application API
    page.route("**/api/draft_application", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"draft": "This is a mock draft based on proposalType: ' + (route.request.post_data_json.get('proposalType', 'None') if route.request.post_data_json else 'None') + '"}'
    ))

    page.goto("http://127.0.0.1:5000/sbir_agent.html")

    # 1. Verify OTA Milestones Section is present
    expect(page.locator("h2:has-text('Execution Milestones (OTA)')")).to_be_visible()

    # 2. Add an OTA milestone
    page.locator("#milestoneName").fill("Hardware Proof-of-Concept Prototype")
    page.locator("#milestoneDate").fill("2024-12-31")
    page.locator("#milestoneDeliverable").fill("Demonstrate sub-10ms socket latency")
    page.locator("#milestoneFunding").fill("$250,000")
    page.locator("#milestoneStatus").select_option("In Progress")
    page.locator("button:has-text('Add Milestone')").click()

    # 3. Verify the milestone is in the list
    milestones_list = page.locator("#milestonesList")
    expect(milestones_list).to_contain_text("Hardware Proof-of-Concept Prototype")
    expect(milestones_list).to_contain_text("In Progress")

    # 4. Search opportunities to test proposal type dropdown
    page.locator("#searchPostedFrom").fill("2024-01-01")
    page.locator("#searchPostedTo").fill("2024-12-31")
    page.locator("button[type='submit']", has_text="Search for Opportunities").click()

    # Wait for result to render
    expect(page.locator("#opportunityResults")).to_contain_text("Test Opportunity 1")

    # Change proposal type in search form to OTA/Milestone-Driven
    page.locator("#proposalTypeSearch").select_option("OTA/Milestone-Driven")

    # Click Draft Application in search results
    page.locator(".draft-btn").first.click()

    # Verify Draft modal opened
    draft_modal = page.locator("#draftModal")
    expect(draft_modal).to_be_visible()

    # Verify draft output contains proposalType from mock server logic
    draft_content = page.locator("#draftModalContent")
    expect(draft_content).to_contain_text("This is a mock draft based on proposalType: OTA/Milestone-Driven")

    # Take a screenshot
    page.screenshot(path="ota_ui_screenshot.png")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
