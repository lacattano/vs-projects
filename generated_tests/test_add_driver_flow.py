import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright, Page, expect

# Define the base URL for the mock insurance site
BASE_URL = "http://localhost:8080/mock_insurance_site.html"

# Define the path for screenshots
SCREENSHOT_DIR = "screenshots"

def generate_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

async def run_tests():
    # Setup directory for screenshots
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    timestamp = generate_timestamp()
    screenshot_prefix = f"test_{timestamp}"
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Take Screenshot: Test Entry
            await page.goto(BASE_URL)
            entry_screenshot_path = f"{SCREENSHOT_DIR}/test_entry_{screenshot_prefix}.png"
            await page.screenshot(path=entry_screenshot_path)
            
            # --- Test Step 1: Enter Driver Name and Licence Number ---
            
            # Locate input fields based on labels (robust strategy)
            driver_name_input = page.get_by_label("Driver Name")
            licence_input = page.get_by_label("Licence Number")
            
            # Fill Driver Name
            await driver_name_input.fill("John Doe")
            fill_name_screenshot_path = f"{SCREENSHOT_DIR}/after_filling_driver_name_{screenshot_prefix}.png"
            await page.screenshot(path=fill_name_screenshot_path)
            
            # Fill Licence Number
            await licence_input.fill("DL-123456")
            fill_licence_screenshot_path = f"{SCREENSHOT_DIR}/after_filling_licence_{screenshot_prefix}.png"
            await page.screenshot(path=fill_licence_screenshot_path)
            
            # --- Test Step 2: Verify Save Vehicle is Disabled ---
            
            save_vehicle_btn = page.get_by_role("button", name="Save Vehicle")
            
            # Check initial state is disabled
            await expect(save_vehicle_btn).not_to_be_enabled()
            
            # --- Test Step 3: Click Add Driver ---
            
            add_driver_btn = page.get_by_role("button", name="Add Driver")
            
            # Take screenshot before adding
            before_add_screenshot_path = f"{SCREENSHOT_DIR}/before_adding_driver_{screenshot_prefix}.png"
            await page.screenshot(path=before_add_screenshot_path)
            
            # Click Add Driver
            await add_driver_btn.click()
            
            # Take screenshot after addition
            after_add_screenshot_path = f"{SCREENSHOT_DIR}/after_adding_driver_{screenshot_prefix}.png"
            await page.screenshot(path=after_add_screenshot_path)
            
            # --- Test Step 4: Verify Driver Added and Save Button Enabled ---
            
            # Verify Driver is in list
            driver_row = page.get_by_role("row", name="John Doe")
            await expect(driver_row).to_be_visible()
            
            # Verify Save Vehicle button is now enabled
            await expect(save_vehicle_btn).to_be_enabled()
            
            # Take Screenshot: Test Passed
            passed_screenshot_path = f"{SCREENSHOT_DIR}/test_passed_{screenshot_prefix}.png"
            await page.screenshot(path=passed_screenshot_path)
            
            print("Test completed successfully.")
            
        except Exception as e:
            # Take Screenshot: Test Failed
            failed_screenshot_path = f"{SCREENSHOT_DIR}/test_failed_{screenshot_prefix}.png"
            await page.screenshot(path=failed_screenshot_path)
            print(f"Test failed with error: {e}")
            raise e
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tests())