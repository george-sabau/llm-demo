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

if __name__ == "__main__":
    # Settings
    MODEL_FILE = './rwa_semantic_model_100d.bin'
    
    QUERY = "sucro 40x40 granit"
    PRODUCT = "casafino stufenplatte siano scuro terrassenplatte gartenplatte betonplatte 40x40"

    print("Vergleiche...")
    print(f"Q: {QUERY}")
    print(f"P: {PRODUCT}")

    score = calculate_semantic_similarity(MODEL_FILE, QUERY, PRODUCT)

    if score is not None:
        print("-" * 33)
        print(f"Semantische Ähnlichkeit: {score}")
        print("-" * 33)