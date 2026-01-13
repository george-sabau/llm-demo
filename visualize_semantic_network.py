import fasttext
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import os

def plot_connected_semantic_network(model_path, num_words=70, num_clusters=7):
    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found.")
        return

    print("Mapping 3+1 Spacetime: Connecting the Colony...")
    model = fasttext.load_model(model_path)

    # 1. Data Prep
    words, freqs = model.get_words(include_freq=True)
    words = words[:num_words]
    freqs = freqs[:num_words]
    vectors = np.array([model.get_word_vector(w) for w in words])

    # 2. Clustering & Sizes
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(vectors)
    size_values = np.log(freqs)
    sizes = ((size_values - size_values.min()) / (size_values.max() - size_values.min())) * 2000 + 300

    # 3. Projection to 2D
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, num_words-1), init='pca')
    coords = tsne.fit_transform(vectors)

    # 4. Relationship Logic
    sim_matrix = cosine_similarity(vectors)

    # 5. Plotting
    plt.figure(figsize=(16, 12))
    plt.style.use('default')
    ax = plt.gca()

    # Draw Connecting Arrows
    for i in range(num_words):
        # Find the word most similar to current word (the 'pull' direction)
        nearest_idx = np.argsort(sim_matrix[i])[-2]

        if sim_matrix[i][nearest_idx] > 0.25:
            start = coords[i]
            end = coords[nearest_idx]

            # Calculate the full distance to connect the bubbles
            dx = end[0] - start[0]
            dy = end[1] - start[1]

            # We use fancy_arrow patches for better control over 'connection'
            ax.annotate("",
                        xy=end,      # Tip of the arrow (Target Bubble)
                        xytext=start, # Base of the arrow (Source Bubble)
                        arrowprops=dict(
                            arrowstyle="->",      # Simple pointer
                            color="black",
                            alpha=0.15,           # Faint relationship line
                            lw=0.6,               # Thin filament
                            mutation_scale=10     # Controls the size of the arrow head
                        ))

    # Draw Bubbles
    plt.scatter(coords[:, 0], coords[:, 1],
                s=sizes,
                c=cluster_labels,
                cmap='tab10',
                alpha=0.5,
                edgecolors='black',
                linewidth=0.3)

    # 6. Labels with slight offset
    for i, word in enumerate(words):
        plt.text(coords[i, 0] + 0.12, coords[i, 1] + 0.12, word,
                 fontsize=8, weight='semibold', color='black')

    plt.title("Semantic Colony: Connected Relationships", fontsize=15)
    plt.axis('off')

    plt.savefig("connected_bubble_map.png", dpi=300, bbox_inches='tight')
    print("Success! Your connected map is ready.")
    plt.show()

if __name__ == "__main__":
    MODEL_FILE = 'fasttext_project/rwa_semantic_model_100d.bin'
    plot_connected_semantic_network(MODEL_FILE)