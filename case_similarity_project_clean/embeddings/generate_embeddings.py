import pickle
from sentence_transformers import SentenceTransformer

from data.load_dataset import load_cjpe
from utils.text_preprocessing import clean_text


def generate_case_embeddings(limit=None):
    """
    Loads CJPE dataset, cleans text, and generates embeddings.

    Args:
        limit (int): limit number of samples (for testing)

    Saves:
        embeddings/case_embeddings.pkl
    """
    print("Loading dataset...")
    dataset = load_cjpe(limit=limit)

    print("Cleaning case texts...")
    texts = [clean_text(sample["text"]) for sample in dataset]

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Generating embeddings...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32
    )

    with open("embeddings/case_embeddings.pkl", "wb") as f:
        pickle.dump((dataset, embeddings), f)

    print("Embeddings saved successfully")


if __name__ == "__main__":
    # For testing, keep limit small
    generate_case_embeddings(limit=None)
