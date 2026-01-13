import re
import os

# 1. Comprehensive Stopword List
GERMAN_STOPWORDS = {
    'der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einer', 'eines', 'einem', 'einen',
    'und', 'oder', 'mit', 'von', 'nach', 'bei', 'fuer', 'für', 'an', 'am', 'im', 'in', 'aus',
    'auf', 'zu', 'zum', 'zur', 'als', 'wie', 'um', 'ueber', 'über', 'vor', 'durch',
    'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'mein', 'dein', 'sein', 'unser', 'euer',
    'ihre', 'diese', 'dieser', 'dieses', 'diesen', 'diesem', 'welche', 'welcher', 'welches',
    'inkl', 'inklusive', 'zzgl', 'ca', 'etwa', 'bitte', 'siehe', 'abb', 'art', 'nr', 'nummer',
    'stk', 'stueck', 'stück', 'pos', 'position', 'mfg', 'u', 'v', 'wird', 'ist', 'sind',
    'war', 'wurde', 'ausser', 'außer', 'ohne', 'ab', 'bis', 'seit'
}

def heavy_duty_sanitize(text):
    # 1. Lowercase & Initial Clean
    text = text.lower()

    # 2. Remove specific symbols: °, quotes, registered marks, pipes, commas, and parentheses
    text = re.sub(r"[|,\"®™'„“”«»!+&°()\[\]]", " ", text)

    # 3. Handle Decimals: convert comma to dot (10,5 -> 10.5)
    text = re.sub(r"(\d+),(\d+)", r"\1.\2", text)

    # 4. Fuse Dimensions (60x40x3.8cm) - keep 'x' only between numbers
    text = re.sub(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)", r"\1x\2", text)
    text = re.sub(r"(\d+x\d+)\s*x\s*(\d+(?:\.\d+)?)", r"\1x\2", text)

    # 5. Fuse Units (Number + Unit) including Power (W/Watt)
    # This attaches 'w' or 'watt' directly to the number: 6 w -> 6w
    units = r"(kg|g|l|w|watt|m|cm|mm|stk|er|stufen|v|ah|mah)"
    text = re.sub(r"(\d+(?:\.\d+)?)\s*" + units + r"\b", r"\1\2", text)

    # 6. Remove standalone punctuation: - and . and /
    # This keeps them if they are inside words (like 10.5kg) but removes them if they are noise
    text = re.sub(r"(?<!\d)[-./]|[ -./](?!\d)", " ", text)

    # 7. Token-based filtering
    tokens = text.split()
    clean_tokens = []
    for t in tokens:
        # Strip remaining dashes or dots from the edges of words
        t = t.strip("-.")

        if (t not in GERMAN_STOPWORDS and
                not t.isdigit() and
                len(t) > 1):
            clean_tokens.append(t)

    return " ".join(clean_tokens)

def process_file(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Fehler: {input_path} nicht gefunden.")
        return

    print(f"Starte Bereinigung: {input_path}...")

    with open(input_path, 'r', encoding='utf-8') as f_in, \
            open(output_path, 'w', encoding='utf-8') as f_out:

        line_count = 0
        for line in f_in:
            cleaned_line = heavy_duty_sanitize(line)
            if cleaned_line.strip():
                f_out.write(cleaned_line + '\n')

            line_count += 1
            if line_count % 1000 == 0:
                print(f"{line_count} Zeilen verarbeitet...", end='\r')

    print(f"\nErfolg! Bereinigte Datei: {output_path}")

if __name__ == "__main__":
    INPUT_FILE = 'domain_corpus.txt'
    OUTPUT_FILE = 'domain_corpus_clean.txt'
    process_file(INPUT_FILE, OUTPUT_FILE)