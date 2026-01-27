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


def search_in_model_vocabulary(model_path, query_word, top_n=10):
    if not os.path.exists(model_path):
        print(f"Fehler: Modell {model_path} nicht gefunden.")
        return

    print(f"Lade Modell {model_path}...")
    model = fasttext.load_model(model_path)

    # get_nearest_neighbors liefert eine Liste von (Score, Wort)
    print(f"Suche nach nächsten Nachbarn für: '{query_word}'...")
    neighbors = model.get_nearest_neighbors(query_word, k=top_n)

    print("\n" + "=" * 50)
    print(f"TOP {top_n} SEMANTISCHE NACHBARN IM MODELL")
    print("=" * 50)

    for score, word in neighbors:
        print(f"[{score:.4f}] {word}")

    print("=" * 50)

import fasttext
import os

def inspect_fasttext_dimension(
        model_path: str,
        word: str,
        dimension: int,
        top_n: int = 20
):
    """
    Inspect a single FastText embedding dimension for a given word.
    Shows:
      - the word's value in that dimension
      - closest words by value in that dimension
      - strongest positive & negative words in that dimension
    """

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    print("Loading FastText model...")
    model = fasttext.load_model(model_path)

    if word not in model.get_words():
        raise ValueError(f"Word '{word}' not in model vocabulary")

    # --- Target word ---
    target_vec = model.get_word_vector(word)
    target_value = target_vec[dimension]

    print("\n" + "=" * 70)
    print(f"WORD: '{word}'")
    print(f"DIMENSION: {dimension}")
    print(f"VALUE: {target_value:+.6f}")
    print("=" * 70)

    # --- Scan vocabulary ---
    scores = []
    for w in model.get_words():
        vec = model.get_word_vector(w)
        scores.append((w, vec[dimension]))

    # --- Closest in this dimension ---
    scores_by_distance = sorted(
        scores,
        key=lambda x: abs(x[1] - target_value)
    )

    print("\nClosest words in this dimension:")
    print("-" * 70)
    for w, v in scores_by_distance[:top_n]:
        delta = v - target_value
        print(f"{v:+.6f}  Δ={delta:+.6f}  {w}")

    # --- Extremes ---
    scores_sorted = sorted(scores, key=lambda x: x[1])

    print("\n" + "=" * 70)
    print("Most positive values:")
    print("-" * 70)
    for w, v in scores_sorted[-10:][::-1]:
        print(f"{v:+.6f}  {w}")

    print("\nMost negative values:")
    print("-" * 70)
    for w, v in scores_sorted[:10]:
        print(f"{v:+.6f}  {w}")

    print("\nDone ✅")


if __name__ == "__main__":
    # Settings
    MODEL_FILE = './rwa_semantic_model_100d.bin'

    # Example: Semantic Similarity between two Queries
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

    # Example: Nearest Neighbours for Query/Word in Model
    search_in_model_vocabulary(MODEL_FILE, "wandschlauchbox", top_n=10)

    # Example: Inspect specific Model Dimension for Query/Word
    inspect_fasttext_dimension(
        model_path=MODEL_FILE,
        word="verzinkt",
        dimension=0,
        top_n=10
    )
