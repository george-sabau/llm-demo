import fasttext
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

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

if __name__ == "__main__":
    # Pfad zu deinem fertigen Modell
    MODEL_FILE = 'fasttext_project/rwa_semantic_model_100d.bin'
    plot_from_bin(MODEL_FILE, num_words=50)