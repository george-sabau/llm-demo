import fasttext
import fasttext.util
import os
import gc

# --- KONFIGURATION ---
RAW_CORPUS_FILE = '../domain_corpus_v2.txt'
CLEAN_CORPUS_FILE = '../domain_corpus_v2_clean.txt'

BASE_MODEL_PATH = '../cc.de.300.bin'
REDUCED_MODEL_PATH = 'cc.de.100.bin'
REDUCED_VEC_PATH = 'cc.de.100.vec'
FINAL_MODEL_NAME = 'rwa_semantic_model_100d.bin'
WORD_LIMIT = 100000 #

def prepare_corpus(input_file, output_file):
    print(f"--- Bereinige Korpus: {input_file} -> {output_file} ---")
    kept = 0
    skipped = 0

    with open(input_file, 'r', encoding='utf-8') as fin, \
            open(output_file, 'w', encoding='utf-8') as fout:

        for line in fin:
            line = line.strip()
            if not line:
                skipped += 1
                continue

            if '||' not in line:
                skipped += 1
                continue

            _, text = line.split('||', 1)
            text = text.strip()

            if not text:
                skipped += 1
                continue

            fout.write(text + "\n")
            kept += 1

    print(f"✔ Behaltene Zeilen: {kept}")
    print(f"✘ Übersprungene Zeilen: {skipped}")

def train_model():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # 1. Basis-Modell vorbereiten
    if not os.path.exists(REDUCED_MODEL_PATH):
        print("--- Reduziere Facebook-Modell auf 100d... ---")
        ft = fasttext.load_model(BASE_MODEL_PATH)
        fasttext.util.reduce_model(ft, 100)
        ft.save_model(REDUCED_MODEL_PATH)
        del ft
        gc.collect()


    # 2. Konvertierung .bin -> .vec (Limit auf 1 Mio. Wörter)
    if not os.path.exists(REDUCED_VEC_PATH):
        print(f"--- Konvertiere in Textformat (Limit: {WORD_LIMIT} Wörter)... ---")
        model = fasttext.load_model(REDUCED_MODEL_PATH)
        words = model.get_words()

        # Sicherstellen, dass wir nicht mehr Wörter anfragen als da sind
        actual_limit = min(len(words), WORD_LIMIT)
        subset_words = words[:actual_limit]

        with open(REDUCED_VEC_PATH, 'w', encoding='utf-8') as f:
            f.write(f"{actual_limit} 100\n")
            for word in subset_words:
                vector = model.get_word_vector(word)
                # Kürzen der Nachkommastellen spart massiv Zeit beim Schreiben/Lesen der .vec
                vector_str = " ".join([f"{v:.6f}" for v in vector])
                f.write(f"{word} {vector_str}\n")
        del model
        gc.collect()

    # 2.5
    if not os.path.exists(CLEAN_CORPUS_FILE):
        prepare_corpus(RAW_CORPUS_FILE, CLEAN_CORPUS_FILE)

    # 3. Fine-Tuning
    print(f"--- Starte Fine-Tuning mit {CLEAN_CORPUS_FILE} ---")
    # minCount=2 filtert "Einmal-Fehler" aus deinem Katalog
    model = fasttext.train_unsupervised(
        input=CLEAN_CORPUS_FILE,
        model='skipgram',
        dim=100,
        epoch=30,
        lr=0.05,
        minn=3,
        maxn=6,
        minCount=2,
        pretrainedVectors=REDUCED_VEC_PATH
    )

    # 4. Speichern (Ohne Quantize, da Unsupervised nicht unterstützt)
    model.save_model(FINAL_MODEL_NAME)

    size_mb = os.path.getsize(FINAL_MODEL_NAME) / (1024*1024)
    print("------------------------------------------------")
    print(f"ERFOLG! Modell: {FINAL_MODEL_NAME}")
    print(f"Finale Größe: {size_mb:.2f} MB")
    print(f"Wortschatz: {len(model.get_words())} Wörter")
    print("------------------------------------------------")

if __name__ == "__main__":
    train_model()