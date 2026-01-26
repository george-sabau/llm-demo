import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

USERNAME = "ges@foryouandyourcustomers.com"
PASSWORD = "1234"

LOGIN_URL = "https://qportal.rwa-test.at/login"
PRODUCT_URL_TEMPLATE = "https://qportal.rwa-test.at/shop/articledetails/01/{article_code}"

UNWANTED_LABELS = [
    "RWA-Nr", "EAN", "Lieferantenartikelnummer", "OTN"
]

UNWANTED_TABLE_COLUMNS = [
    "Art.Nr.", "OTN/LiefArtNr"
]

UNWANTED_TEXTS = [
    "Varianten ausblenden",
    "Alle Artikelausprägungen",
    "Artikel abonnieren",
    "Großes Bild anzeigen",
    "L/S", "UVP/EH", "Menge", "Lager/Strecke","Liefermengeneinheit",
    "Basismengeneinheit","Marke","Gewicht brutto","Lieferant/Fabrikat","Lieferant"
]

# ----------------------------
# TEXT CLEANING
# ----------------------------
def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # 1. Remove divs with specific class prefix
    for div in soup.find_all("div", class_=lambda c: c and any(cls.startswith("column-format--COMPONENT") for cls in c if cls)):
        div.decompose()

    # 2. Remove all <h3> elements
    for h3 in soup.find_all("h3"):
        h3.decompose()

    # 3. Remove small elements with unwanted keywords
    unwanted_keywords = ["TA", "Merkzettel 1", "Merkzettel 2", "MZ1", "MZ2", "Tag"]
    for elem in soup.find_all(lambda tag: tag.name in ["div", "span"]):
        text = elem.get_text(strip=True)
        if text in unwanted_keywords:
            elem.decompose()

    # 4. Remove <strong> labels in UNWANTED_LABELS
    for strong in soup.find_all("strong"):
        label = strong.get_text(strip=True)
        if label in UNWANTED_LABELS:
            parent_div = strong.find_parent("div")
            if parent_div:
                parent_div.decompose()

    # 5. Remove empty divs
    for div in soup.find_all("div"):
        if not div.get_text(strip=True).replace("\xa0", ""):
            div.decompose()

    # 6. Remove unwanted table columns
    for table in soup.find_all("table"):
        thead = table.find("thead")
        if not thead:
            continue

        headers = [th.get_text(strip=True) for th in thead.find_all("th")]
        remove_indexes = [i for i, h in enumerate(headers) if h in UNWANTED_TABLE_COLUMNS]
        remove_indexes.sort(reverse=True)

        for i in remove_indexes:
            ths = thead.find_all("th")
            if i < len(ths):
                ths[i].decompose()

        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            for i in remove_indexes:
                if i < len(cells):
                    cells[i].decompose()

    # 7. Extract text
    text = soup.get_text(separator="\n", strip=True)

    # 8. Remove unwanted phrases
    for phrase in UNWANTED_TEXTS:
        text = text.replace(phrase, "")

    # 9. Remove empty/noise lines
    text = "\n".join(line for line in text.splitlines() if line.strip())

    return text

# ----------------------------
# TOKENIZER
# ----------------------------
def tokenize(text: str):
    token_pattern = re.compile(r"""
        \b
        (?:[\w€]+(?:[-.,/]\w+)*)
        \b
    """, re.VERBOSE)

    tokens = token_pattern.findall(text)

    # Deduplicate while preserving order
    seen = set()
    unique_tokens = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique_tokens.append(t)

    return " ".join(unique_tokens)

# ----------------------------
# FETCH PRODUCT
# ----------------------------
def fetch_product_details(page, article_code: str):
    page.goto(PRODUCT_URL_TEMPLATE.format(article_code=article_code))
    page.wait_for_load_state("networkidle")

    root_div = page.query_selector("#root")
    if not root_div:
        return None

    html = root_div.inner_html()
    return clean_html(html)

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    input_file = "domain_corpus_pdp_candidates.csv"  # input file: articleCode,baseProductCode per line
    output_file = "domain_corpus_clean_v2.text"

    # Read input
    with open(input_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Start Playwright session
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # LOGIN
        page.goto(LOGIN_URL)

        page.fill('input[placeholder="E-mail Adresse"]', USERNAME)
        page.fill('input[placeholder="Passwort"]', PASSWORD)

        # Use locator with increased timeout
        locator = page.locator('button:has-text("Login")')
        locator.wait_for(state="visible", timeout=60000)  # wait up to 60s
        locator.click()

        page.wait_for_load_state("networkidle")

        # Open output file
        with open(output_file, "w", encoding="utf-8") as out_f:
            for line in lines:
                article_code, base_product_code = line.split(",", 1)

                try:
                    cleaned_text = fetch_product_details(page, article_code)
                    if not cleaned_text:
                        continue

                    tokenized_text = tokenize(cleaned_text)
                    out_f.write(f"{base_product_code}||{tokenized_text}\n")
                    print(f"Processed {article_code} -> {base_product_code}")
                except Exception as e:
                    print(f"ERROR processing {article_code}: {e}")

        browser.close()
