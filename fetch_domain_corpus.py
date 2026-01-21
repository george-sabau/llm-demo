import requests
import json
import re
import os

# --- CONFIGURATION ---
BASE_URL = "http://lcsrvrwa006.rwa-test.at:8983/solr/master_PortalIndex_BaseProduct_default/select"
OUTPUT_FILE = "fasttext_project/domain_corpus.txt"
ROWS_PER_PAGE = 2000
TOTAL_ROWS = 163238

# Fields we want to extract
FIELDS = ["brand_string", "seoText_text_de_mv", "name_text_de", "allVariantNames_text_de_mv", "otns_string_mv","description_dext_de", "allReferenceNames_text_de_mv", "allVariantNames_text_de_mv"]

def clean_and_export():
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # We use a set for global line deduplication (if memory allows)
    # If the file is too huge, we'll write first and dedup later.
    global_seen_lines = set()

    print(f"Starting Solr export to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for start in range(0, TOTAL_ROWS + 1, ROWS_PER_PAGE):
            print(f"Processing {start} to {start + ROWS_PER_PAGE}...")
            
            # 1. Build Request
            params = {
                "fl": ",".join(FIELDS),
                "indent": "true",
                "q.op": "OR",
                "q": "*:*",
                "rows": ROWS_PER_PAGE,
                "start": start,
                "wt": "json"
            }

            try:
                response = requests.get(BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                docs = data.get("response", {}).get("docs", [])

                for doc in docs:
                    raw_parts = []
                    for field in FIELDS:
                        val = doc.get(field, "")
                        if isinstance(val, list):
                            raw_parts.extend([str(v) for v in val])
                        else:
                            raw_parts.append(str(val))

                    # 2. Lowercase and Basic Cleaning
                    full_text = " ".join(raw_parts).lower()
                    full_text = full_text.replace("|", " ") # Remove pipes
                    
                    # 3. Deduplicate words within the line
                    # Using a dict to maintain order while removing duplicates
                    words = full_text.split()
                    unique_words = list(dict.fromkeys(words))
                    
                    clean_line = " ".join(unique_words).strip()

                    # 4. Global line deduplication
                    if len(clean_line) > 1 and clean_line not in global_seen_lines:
                        f.write(clean_line + "\n")
                        global_seen_lines.add(clean_line)

            except Exception as e:
                print(f"Error at start {start}: {e}")
                continue

    print(f"Finished! Clean corpus saved in {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_and_export()