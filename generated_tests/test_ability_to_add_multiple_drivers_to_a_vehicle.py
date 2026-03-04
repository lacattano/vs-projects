# Auto-generated test for: ability to add multiple drivers to a vehicle
# Generated on: 2026-03-03 14:41:38.273600
#
# The locators in this test may need to be adjusted to match your current application.

from playwright.sync_api import Page, expect


class AddMultipleDriversPage:
    def __init__(self, page):
        self.page = page
        self.input_name = page.locator("#input-name")
        self.button_submit = page.get_by_role("button", name="Add Driver")

    def fill_form(self, name: str):
        self.input_name.fill(name)


def test_ability_to_add_multiple_drivers_to_a_vehicle(page: Page):
    page.goto("https://example.com/add-drivers")

    # Test steps here
    expect(self.page.get_by_text("Multiple Drivers")).to_be_visible()
