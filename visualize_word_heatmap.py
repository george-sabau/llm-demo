import os

import fasttext
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_from_bin(model_path, num_words=50):
    if not os.path.exists(model_path):
        print(f"Fehler: Datei {model_path} nicht gefunden.")
        return

    print(f"Lade Modell {model_path}...")
    model = fasttext.load_model(model_path)

    # Die am häufigsten vorkommenden Wörter abrufen
    words = model.get_words()[:num_words]
    vectors = [model.get_word_vector(w) for w in words]

    # Daten für die Heatmap aufbereiten
    df = pd.DataFrame(vectors, index=words)

    # Plot erstellen
    plt.figure(figsize=(16, 10))
    # 'coolwarm' oder 'RdBu_r' sind gut, um positive/negative Werte zu sehen
    sns.heatmap(df, cmap='coolwarm', center=0)

    plt.title(f"Semantische Heatmap: {model_path} (Top {num_words} Wörter)")
    plt.xlabel("Vektor-Dimension (1-100)")
    plt.ylabel("Wort aus deinem Katalog / FB-Basis")

    output_name = "rwa_model_heatmap.png"
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    print(f"Erfolg! Heatmap wurde als {output_name} gespeichert.")
    plt.show()

def inspect_dimension(model_path: str, word: str, dim: int = 9, top_n: int = 10) -> None:
    """
    Inspect a single dimension of a FastText word vector.

    Args:
        model_path (str): Path to the FastText .bin model
        word (str): Word to inspect
        dim (int): Dimension to inspect (1-based)
        top_n (int): Number of top closest/positive/negative words to show
    """
    # Load model
    model = fasttext.load_model(model_path)

    # Convert 1-based dim to 0-based index
    dim_idx = dim - 1

    # Get vector for the word
    vec = model.get_word_vector(word)
    print(f"Word '{word}' has value {vec[dim_idx]:.4f} in dimension {dim}")

    # Build dict of all words vs. this dimension
    words = model.get_words()
    dim_values = {w: model.get_word_vector(w)[dim_idx] for w in words}

    # Closest words in this single dimension
    closest = sorted(dim_values.items(), key=lambda x: abs(x[1] - vec[dim_idx]))[:top_n]
    print(f"\nTop {top_n} words closest to '{word}' in dimension {dim}:")
    for w, v in closest:
        print(f"{w}: {v:.4f}")

    # Top positive values in this dimension
    most_positive = sorted(dim_values.items(), key=lambda x: -x[1])[:top_n]
    print(f"\nTop {top_n} words with highest values in dimension {dim}:")
    for w, v in most_positive:
        print(f"{w}: {v:.4f}")

    # Top negative values in this dimension
    most_negative = sorted(dim_values.items(), key=lambda x: x[1])[:top_n]
    print(f"\nTop {top_n} words with lowest values in dimension {dim}:")
    for w, v in most_negative:
        print(f"{w}: {v:.4f}")

if __name__ == "__main__":
    # Pfad zu deinem fertigen Modell
    MODEL_FILE = 'fasttext_project/rwa_semantic_model_100d.bin'
    inspect_dimension(MODEL_FILE, word="passend", dim=9, top_n=10)
    plot_from_bin(MODEL_FILE, num_words=50)