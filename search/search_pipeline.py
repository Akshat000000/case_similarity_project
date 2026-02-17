import math
from search.semantic_search_db import SemanticSearcherDB
from rerank.cross_encoder_reranker import CrossEncoderReranker


# ==================================================
# Ranking Weights (sum = 1.0)
# ==================================================
EMBEDDING_WEIGHT = 0.5
CROSS_ENCODER_WEIGHT = 0.3
DECISION_WEIGHT = 0.15
REASONING_WEIGHT = 0.05


class CaseSearchPipeline:
    """
    Multi-stage case search pipeline:
    1) Embedding retrieval
    2) Cross-encoder reranking
    3) Weighted explainable scoring
    """

    def __init__(self):
        self.retriever = SemanticSearcherDB()
        self.reranker = CrossEncoderReranker()

    # --------------------------------------------------
    # Helper functions
    # --------------------------------------------------
    def _decision_score(self, decision):
        return 1.0 if decision == "accepted" else 0.7

    def _reasoning_score(self, reason):
        return 1.0 if reason else 0.8

    def _sigmoid(self, x):
        """Normalize cross-encoder logits to 0–1"""
        return 1 / (1 + math.exp(-x))

    # --------------------------------------------------
    # Main search
    # --------------------------------------------------
    def search(self, query_text):

        # Stage 1: Retrieve
        candidates = self.retriever.retrieve(
            query_text=query_text,
            top_k=10
        )

        if not candidates:
            return []

        # Stage 2: Cross-encoder rerank
        reranked = self.reranker.rerank(
            query_text=query_text,
            candidates=candidates,
            top_k=10
        )

        # Stage 3: Weighted scoring
        final_results = []

        for c in reranked:
            embed_score = float(c.get("embed_score", 0.0))

            raw_cross = float(c.get("cross_score", 0.0))
            cross_score = self._sigmoid(raw_cross)

            decision = c.get("decision")
            reason = c.get("decision_reason")

            embed_contrib = EMBEDDING_WEIGHT * embed_score
            cross_contrib = CROSS_ENCODER_WEIGHT * cross_score
            decision_contrib = DECISION_WEIGHT * self._decision_score(decision)
            reason_contrib = REASONING_WEIGHT * self._reasoning_score(reason)

            final_score = (
                embed_contrib +
                cross_contrib +
                decision_contrib +
                reason_contrib
            )

            # Store breakdown for UI
            c["score_breakdown"] = {
                "embedding": round(embed_contrib, 4),
                "cross_encoder": round(cross_contrib, 4),
                "decision": round(decision_contrib, 4),
                "reasoning": round(reason_contrib, 4),
            }

            c["final_score"] = round(final_score, 4)

            final_results.append(c)

        final_results = sorted(
            final_results,
            key=lambda x: x["final_score"],
            reverse=True
        )

        return final_results[:5]
