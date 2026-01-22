import os
import spacy
from bs4 import BeautifulSoup
import re

# Load SpaCy blank German model
nlp = spacy.blank("de")

def clean_html(text: str) -> str:
    """Remove HTML tags using BeautifulSoup."""
    return BeautifulSoup(text, "html.parser").get_text(separator=" ")

def classic_tokenize(text: str):
    """SpaCy-based Lucene Classic-style tokenizer."""
    doc = nlp(text)
    tokens = [
        t.text for t in doc
        if t.is_alpha or t.is_digit  # keep letters & digits
    ]

    # Remove duplicates while preserving order
    seen = set()
    unique_tokens = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique_tokens.append(t)

    return unique_tokens

def heavy_duty_sanitize(text: str):
    # 1. HTML cleanup
    text = clean_html(text)

    # 2. Remove special characters except letters/digits
    text = re.sub(r"[|,\"®™'„“”«»!+&°()\[\];:/\-]", " ", text)

    # 3. Handle decimals (10,5 -> 10.5)
    text = re.sub(r"(\d+),(\d+)", r"\1.\2", text)

    # 4 Tokenize with SpaCy classic tokenizer
    tokens = classic_tokenize(text)

    return " ".join(tokens)

def process_file(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Fehler: {input_path} nicht gefunden.")
        return

    print(f"Starte Bereinigung: {input_path}...")

    with open(input_path, 'r', encoding='utf-8') as f_in, \
            open(output_path, 'w', encoding='utf-8') as f_out:

        for i, line in enumerate(f_in, start=1):
            cleaned_line = heavy_duty_sanitize(line)
            if cleaned_line.strip():
                f_out.write(cleaned_line + '\n')

            if i % 1000 == 0:
                print(f"{i} Zeilen verarbeitet...", end='\r')

    print(f"\nErfolg! Bereinigte Datei: {output_path}")

if __name__ == "__main__":
    INPUT_FILE = 'domain_corpus.txt'
    OUTPUT_FILE = 'domain_corpus_clean.txt'
    process_file(INPUT_FILE, OUTPUT_FILE)
