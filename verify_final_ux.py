import re
from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:5000/sbir_agent.html")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("SBIR Grant Agent"))

    # 1. Verify the tabbed interface
    search_tab = page.locator("#tab-search")
    profile_tab = page.locator("#tab-profile")
    search_content = page.locator("#content-search")
    profile_content = page.locator("#content-profile")

    # Initially, Search tab should be active and its content visible
    expect(search_tab).to_have_class(re.compile("active"))
    expect(search_content).to_be_visible()
    expect(profile_content).to_be_hidden()

    # 2. Click on the Profile tab
    profile_tab.click()

    # Now, Profile tab should be active and its content visible
    expect(profile_tab).to_have_class(re.compile("active"))
    expect(search_content).to_be_hidden()
    expect(profile_content).to_be_visible()

    # 3. Verify the footer is present
    footer = page.locator("footer")
    expect(footer).to_be_visible()
    expect(footer).to_contain_text("SBIR Grant Agent - © 2024. Licensed under GPLv3.")

    # 4. Take a screenshot of the final state
    page.screenshot(path="final_ux_screenshot.png")

    # 5. Close context and browser
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)