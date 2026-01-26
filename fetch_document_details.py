import requests
from playwright.sync_api import sync_playwright

# SSO credentials
USERNAME = "ges@foryouandyourcustomers.com"
PASSWORD = "1234"
CLIENT_ID  ="react_client"
CLIENT_SECRET  ="secret"
TOKEN_URL = "https://qb2b-api.rwa-test.at/authorizationserver/oauth/token"
PRODUCT_URL = "https://qportal.rwa-test.at/shop/articledetails/01/29660924"
LOGIN_URL = "https://qportal.rwa-test.at/login"


def get_token():
    data = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    r = requests.post(TOKEN_URL, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

def fetch_product_details():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False helps debug login
        page = browser.new_page()

        # Step 1: Go to login page
        page.goto(LOGIN_URL)

        # Step 2: Fill in login form
        page.fill('input[placeholder="E-mail Adresse"]', USERNAME)
        page.fill('input[placeholder="Passwort"]', PASSWORD)
        # # Wait for SSO button and click it
        page.wait_for_selector("text=Login mit SSO")
        page.click("text=Login mit SSO")

        # Step 3: Wait for redirect after login
        page.wait_for_load_state("networkidle")
        print("Login complete, now going to product page...")

        # Step 4: Go to the protected product page
        page.goto(PRODUCT_URL)
        page.wait_for_load_state("networkidle")

        # Step 5: Grab the #root content
        root_div = page.query_selector("#root")
        html = root_div.inner_html() if root_div else None
        text = root_div.inner_text() if root_div else None

        browser.close()
        return {"html": html, "text": text};

if __name__ == "__main__":
    details = fetch_product_details()
    if details:
        print("HTML inside <div id='root'>:\n", details["html"])
        print("\nPlain text inside <div id='root'>:\n", details["text"])
