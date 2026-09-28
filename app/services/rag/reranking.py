from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(MODEL_NAME)


def rerank(
    query: str,
    results: list,
    top_k: int = 5,
) -> list:
    pairs = [
        (query, result.content)
        for result in results
    ]

    scores = reranker.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):
        reranked.append({
            "result": result,
            "score": float(score),
        })

    reranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return reranked[:top_k]