"""
Captures screenshots of the running Flask app for the report.
"""
import time
import subprocess
import os
from playwright.sync_api import sync_playwright

def capture():
    # Start app.py in background
    app_process = subprocess.Popen(
        ["python", "app.py"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)  # Wait for Flask to boot

    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    os.makedirs(assets_dir, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 800})

            # 1. Dashboard
            page.goto("http://127.0.0.1:5000/")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=os.path.join(assets_dir, "screenshot_dashboard.png"))
            print("Captured screenshot_dashboard.png")

            # 2. Patients Directory
            page.goto("http://127.0.0.1:5000/patients")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=os.path.join(assets_dir, "screenshot_patients.png"))
            print("Captured screenshot_patients.png")

            # 3. Analytics
            page.goto("http://127.0.0.1:5000/analytics")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=os.path.join(assets_dir, "screenshot_analytics.png"))
            print("Captured screenshot_analytics.png")

            # 4. Patient Detail
            page.goto("http://127.0.0.1:5000/patients/PAT-1001")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=os.path.join(assets_dir, "screenshot_patient_detail.png"))
            print("Captured screenshot_patient_detail.png")

            browser.close()
    finally:
        app_process.terminate()
        app_process.wait()
        print("Terminated Flask app")

if __name__ == "__main__":
    capture()
