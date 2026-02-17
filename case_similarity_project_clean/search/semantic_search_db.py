import numpy as np
from sentence_transformers import SentenceTransformer
from database.db_connection import DatabaseConnection


class SemanticSearcherDB:
    """
    Stage-1 Retrieval using sentence embeddings.
    Returns Top-K candidate cases.
    """

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.db = DatabaseConnection()

    @staticmethod
    def cosine_similarity(a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def retrieve(self, query_text, top_k=10):
        """
        Retrieve top-K similar cases using embeddings.
        """

        query_embedding = self.model.encode(query_text).tolist()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                case_id,
                embedding,
                text,
                summary,
                decision,
                decision_reason
            FROM cases;
        """)

        candidates = []

        for row in cursor.fetchall():
            score = self.cosine_similarity(
                query_embedding, row["embedding"]
            )
            
            # Use stored summary if available, else truncate text
            summary_text = row["summary"]
            if not summary_text:
                summary_text = row["text"][:300] + "..."

            candidates.append({
                "case_id": row["case_id"],
                "embed_score": float(score),
                "decision": row["decision"],
                "decision_reason": row["decision_reason"],
                "summary": summary_text,
                "full_text": row["text"]
            })

        cursor.close()
        conn.close()

        # Sort by embedding similarity
        candidates.sort(
            key=lambda x: x["embed_score"],
            reverse=True
        )

        return candidates[:top_k]
