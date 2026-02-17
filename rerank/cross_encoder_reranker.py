from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """
    Cross-encoder re-ranker that PRESERVES candidate metadata.
    """

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(self, query_text, candidates, top_k=10):
        """
        Adds cross_score to each candidate WITHOUT
        losing existing fields.
        """

        if not candidates:
            return []

        # Prepare pairs for cross-encoder
        pairs = [
            (query_text, c.get("full_text", ""))
            for c in candidates
        ]

        scores = self.model.predict(pairs)

        # IMPORTANT: mutate existing candidate dicts
        for candidate, score in zip(candidates, scores):
            candidate["cross_score"] = float(score)

        # Sort by cross-encoder score
        reranked = sorted(
            candidates,
            key=lambda x: x.get("cross_score", 0),
            reverse=True
        )

        return reranked[:top_k]
