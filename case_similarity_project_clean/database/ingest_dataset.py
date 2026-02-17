import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.load_dataset import load_cjpe
from sentence_transformers import SentenceTransformer
from database.db_connection import DatabaseConnection
from tqdm import tqdm


# -----------------------------
# Helper: Map label to decision
# -----------------------------
def map_decision(label):
    """
    Converts dataset label to judicial decision.
    1 -> accepted
    0 -> rejected
    """
    return "accepted" if label == 1 else "rejected"


# -----------------------------
# Helper: Extract decision reason
# -----------------------------
def extract_decision_reason(case):
    """
    Extracts expert-based reasoning from CJPE dataset.
    Uses first 1–2 expert opinions if available.
    """
    reasons = []

    for i in range(1, 6):
        val = case.get(f"expert_{i}")
        if val and isinstance(val, str):
            reasons.append(val.strip())

    return " | ".join(reasons[:2]) if reasons else None


# -----------------------------
# Main ingestion function
# -----------------------------
def ingest_dataset(limit=None):
    """
    Loads CJPE dataset, generates embeddings,
    and inserts cases into PostgreSQL database.

    Args:
        limit (int or None): Number of cases to ingest
                             None = full dataset
    """

    print("[INFO] Loading CJPE dataset...")
    dataset = load_cjpe(limit=limit)

    print("[INFO] Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Connect to PostgreSQL
    db = DatabaseConnection()
    conn = db.get_connection()
    cursor = conn.cursor()

    # PostgreSQL-safe insert query with duplicate protection
    insert_query = """
        INSERT INTO cases (
            case_id,
            embedding,
            text,
            decision,
            decision_reason,
            case_source
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (case_id) DO NOTHING;
    """

    inserted_count = 0

    print("[INFO] Inserting cases into PostgreSQL...")

    for case in tqdm(dataset):

        case_id = case["id"]
        text = case["text"]

        # Skip invalid cases
        if not text or not isinstance(text, str):
            continue

        decision = map_decision(case["label"])
        decision_reason = extract_decision_reason(case)

        # Generate 384-dim embedding (FLOAT8[])
        embedding = model.encode(text).tolist()

        cursor.execute(
            insert_query,
            (
                case_id,
                embedding,
                text,
                decision,
                decision_reason,
                "dataset",
            ),
        )

        inserted_count += 1

        # Commit every 100 records
        if inserted_count % 100 == 0:
            conn.commit()

    # Final commit
    conn.commit()
    cursor.close()
    conn.close()

    print(f"[DONE] Dataset ingestion completed. Inserted {inserted_count} cases.")


# -----------------------------
# Script entry point
# -----------------------------
if __name__ == "__main__":
    ingest_dataset(limit=None)  # None = full dataset
