import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

LEAGUE_ID = "503435"
LEAGUE_URL = f"https://football.fantasysports.yahoo.com/f1/{LEAGUE_ID}"
SESSION_PATH = os.path.join(os.path.dirname(__file__), "session.json")

def authenticate():
    print("=" * 60, flush=True)
    print("YAHOO FANTASY FOOTBALL AUTHENTICATION SETUP", flush=True)
    print("=" * 60, flush=True)
    print(f"Target League: {LEAGUE_URL}", flush=True)
    print(f"Session output: {SESSION_PATH}", flush=True)
    print("\nLaunching browser on your desktop...", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized", "--new-window"])
        context = browser.new_context(viewport=None)
        page = context.new_page()

        print(f"Navigating to {LEAGUE_URL}...", flush=True)
        try:
            page.goto(LEAGUE_URL, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Nav notice: {e}", flush=True)

        print("\n" + "#" * 60)
        print("ACTION: Log into your Yahoo account in the browser.")
        print("Once you are logged in and see the league page, press ENTER in the terminal.")
        print("#" * 60 + "\n", flush=True)

        try:
            input("Press ENTER once you have logged into Yahoo and see the league page: ")
            logged_in = True
        except Exception:
            # If running non-interactively, wait until user is actually on league page (not login page)
            print("Monitoring for successful login...", flush=True)
            logged_in = False
            for i in range(300):
                time.sleep(2)
                try:
                    curr_url = page.url
                    title = page.title()
                    if "fantasysports.yahoo.com" in curr_url and "login" not in curr_url.lower() and "Sign in" not in title and "Sign In" not in title:
                        content = page.content()
                        if "Request denied" not in content and len(content) > 5000:
                            print(f"Detected successful login on {curr_url} (Title: {title})!", flush=True)
                            logged_in = True
                            time.sleep(2)
                            break
                except Exception:
                    pass

        print("Saving session...", flush=True)
        context.storage_state(path=SESSION_PATH)
        browser.close()
        print(f"SUCCESS! Session saved to {SESSION_PATH}", flush=True)

    # Verify
    verify_session()

def verify_session():
    print("\nVerifying headless session...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=SESSION_PATH)
        page = context.new_page()
        try:
            page.goto(LEAGUE_URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            pass
        print(f"Headless URL: {page.url}")
        print(f"Page Title: {page.title()}")
        if "login.yahoo.com" in page.url:
            print("FAILED: Redirected to login. Please run auth_setup.py again.")
            browser.close()
            sys.exit(1)
        else:
            print("SUCCESS: Authenticated session confirmed!")
            browser.close()

if __name__ == "__main__":
    authenticate()
