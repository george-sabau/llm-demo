import asyncio

import aiofiles
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

USERNAME = "ges@foryouandyourcustomers.com"
PASSWORD = "1234"

LOGIN_URL = "https://qportal.rwa-test.at/login"
PRODUCT_URL_TEMPLATE = "https://qportal.rwa-test.at/shop/articledetails/01/{article_code}"

UNWANTED_LABELS = ["RWA-Nr", "EAN", "Lieferantenartikelnummer", "OTN"]
UNWANTED_TABLE_COLUMNS = ["Art.Nr.", "OTN/LiefArtNr"]
UNWANTED_TEXTS = [
    "Varianten ausblenden", "Alle Artikelausprägungen", "Artikel abonnieren",
    "Großes Bild anzeigen", "L/S", "UVP/EH", "Menge", "Lager/Strecke",
    "Liefermengeneinheit","Basismengeneinheit","Marke","Gewicht brutto",
    "Lieferant/Fabrikat","Lieferant"
]

# ----------------------------
# TEXT CLEANING
# ----------------------------
def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for div in soup.find_all("div", class_=lambda c: c and any(cls.startswith("column-format--COMPONENT") for cls in c if cls)):
        div.decompose()
    for h3 in soup.find_all("h3"):
        h3.decompose()
    unwanted_keywords = ["TA", "Merkzettel 1", "Merkzettel 2", "MZ1", "MZ2", "Tag","MO","Monat","FB", "Frühbezug"]
    for elem in soup.find_all(lambda tag: tag.name in ["div", "span"]):
        if elem.get_text(strip=True) in unwanted_keywords:
            elem.decompose()
    for strong in soup.find_all("strong"):
        if strong.get_text(strip=True) in UNWANTED_LABELS:
            parent_div = strong.find_parent("div")
            if parent_div:
                parent_div.decompose()
    for div in soup.find_all("div"):
        if not div.get_text(strip=True).replace("\xa0", ""):
            div.decompose()
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

    text = soup.get_text(separator="\n", strip=True)
    for phrase in UNWANTED_TEXTS:
        text = text.replace(phrase, "")
    text = "\n".join(line for line in text.splitlines() if line.strip())
    return text

# ----------------------------
# TOKENIZER: remove duplicates only
# ----------------------------
def tokenize(text: str):
    words = text.split()  # split by whitespace
    seen = set()
    unique_words = []
    for word in words:
        if word not in seen:
            seen.add(word)
            unique_words.append(word)
    return " ".join(unique_words)

# ----------------------------
# FETCH PRODUCT
# ----------------------------
async def fetch_product_details(context, article_code: str):
    page = await context.new_page()
    try:
        print(f"Fetching article {article_code}...")
        await page.goto(PRODUCT_URL_TEMPLATE.format(article_code=article_code), timeout=60000)
        await page.wait_for_load_state("networkidle")
        root_div = await page.query_selector("#root")
        if not root_div:
            print(f"Article {article_code} has no root div.")
            return None
        html = await root_div.inner_html()
        print(f"Fetched article {article_code} successfully.")
        return clean_html(html)
    except PlaywrightTimeoutError:
        print(f"Timeout fetching article {article_code}")
        return None
    except Exception as e:
        print(f"Failed to fetch article {article_code}: {e}")
        return None
    finally:
        await page.close()

# ----------------------------
# MAIN
# ----------------------------
async def main():
    input_file = "domain_corpus_candidates.csv"
    output_file = "domain_corpus_v2.txt"

    with open(input_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # LOGIN once
        print("Logging in...")
        page = await context.new_page()
        await page.goto(LOGIN_URL)
        await page.fill('input[placeholder="E-mail Adresse"]', USERNAME)
        await page.fill('input[placeholder="Passwort"]', PASSWORD)
        await page.click('button:has-text("Login")')
        await page.wait_for_load_state("networkidle")
        print("Login successful.")
        await page.close()

        semaphore = asyncio.Semaphore(10)  # 10 pages concurrently

        # Open file once for async writing
        async with aiofiles.open(output_file, "w", encoding="utf-8") as out_f:

            async def process_article(line):
                article_code, base_product_code = line.split(",", 1)
                async with semaphore:
                    cleaned_text = await fetch_product_details(context, article_code)
                if not cleaned_text:
                    print(f"Skipping {article_code} due to empty content.")
                    return
                tokenized_text = tokenize(cleaned_text)
                print(f"Processed {article_code} -> {base_product_code}")
                await out_f.write(f"{base_product_code}||{tokenized_text}\n")

            tasks = [process_article(line) for line in lines]
            await asyncio.gather(*tasks)

        await browser.close()
        print("All done!")

if __name__ == "__main__":
    asyncio.run(main())
