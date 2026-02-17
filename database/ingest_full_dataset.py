import sys
import os
import json
from tqdm import tqdm
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# Add project root to path
# --------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import DatabaseConnection


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def map_decision(label):
    return "accepted" if label == 1 else "rejected"


def extract_decision_reason(case):
    reasons = []
    for i in range(1, 6):
        key = f"expert_{i}"
        val = case.get(key)
        if val and isinstance(val, str):
            reasons.append(val.strip())
    return " | ".join(reasons[:2]) if reasons else None


# --------------------------------------------------
# Main ingestion
# --------------------------------------------------
def ingest_all_splits():
    print("\n[INFO] Loading CJPE dataset metadata...")

    dataset_dict = load_dataset("Exploration-Lab/IL-TUR", "cjpe")
    split_names = list(dataset_dict.keys())

    print(f"[INFO] Found splits: {split_names}")

    print("[INFO] Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    db = DatabaseConnection()
    conn = db.get_connection()
    cursor = conn.cursor()

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

    total_inserted = 0

    for split in split_names:
        print(f"\n[INFO] Ingesting split: {split}")
        dataset = dataset_dict[split]

        for case in tqdm(dataset, desc=f"Processing {split}"):
            case_id = case.get("id")
            text = case.get("text")

            if not case_id or not text:
                continue

            decision = map_decision(case.get("label", 0))
            decision_reason = extract_decision_reason(case)

            embedding = model.encode(text).tolist()

            cursor.execute(
                insert_query,
                (
                    case_id,
                    embedding,
                    text,
                    decision,
                    decision_reason,
                    split
                )
            )

            total_inserted += 1

            if total_inserted % 500 == 0:
                conn.commit()

        conn.commit()
        print(f"[DONE] Finished split: {split}")

    cursor.close()
    conn.close()

    print("\n✅ FULL DATASET INGESTION COMPLETED")
    print(f"📊 Total processed cases (before dedup): {total_inserted}")

# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    ingest_all_splits()
