import fasttext
import numpy as np
import os

def calculate_semantic_similarity(model_path, text1, text2):
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found.")
        return None

    # Load the model (only do this once in a real application)
    model = fasttext.load_model(model_path)

    # 1. Get Sentence Vectors
    # FastText handles the tokenization and averaging internally
    vec1 = model.get_sentence_vector(text1)
    vec2 = model.get_sentence_vector(text2)

    # 2. Calculate Cosine Similarity
    # formula: (a · b) / (||a|| * ||b||)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    similarity = np.dot(vec1, vec2) / (norm1 * norm2)

    return round(float(similarity), 4)

import fasttext
import os

def search_in_model_vocabulary(model_path, query_word, top_n=10):
    if not os.path.exists(model_path):
        print(f"Fehler: Modell {model_path} nicht gefunden.")
        return

    print(f"Lade Modell {model_path}...")
    model = fasttext.load_model(model_path)

    # get_nearest_neighbors liefert eine Liste von (Score, Wort)
    print(f"Suche nach nächsten Nachbarn für: '{query_word}'...")
    neighbors = model.get_nearest_neighbors(query_word, k=top_n)

    print("\n" + "="*50)
    print(f"TOP {top_n} SEMANTISCHE NACHBARN IM MODELL")
    print("="*50)

    for score, word in neighbors:
        print(f"[{score:.4f}] {word}")

    print("="*50)

if __name__ == "__main__":
    # Settings
    MODEL_FILE = './rwa_semantic_model_100d.bin'
    
    QUERY = "gardena wandschlauchbox"
    PRODUCT = "Gardena Steckerladegerät"

    print("Vergleiche...")
    print(f"Q: {QUERY}")
    print(f"P: {PRODUCT}")

    score = calculate_semantic_similarity(MODEL_FILE, QUERY, PRODUCT)

    if score is not None:
        print("-" * 33)
        print(f"Semantische Ähnlichkeit: {score}")
        print("-" * 33)

    search_in_model_vocabulary(MODEL_FILE, "wandschlauchbox", top_n=10)