from golden_dataset import golden_dataset 
from sales_agent import chat_with_sales_agent 
from langfuse_config import langfuse
from evaluators import ( 
evaluate_correctness, 
evaluate_relevance, 
evaluate_hallucination, 
evaluate_groundedness,
run_agent_for_eval 
) 
from langfuse import get_client
langfuse = get_client()
    




# ============================================================
# SCORE STORAGE
# ============================================================

correctness_scores = []
relevance_scores = []
hallucination_scores = []
groundedness_scores = []


# ============================================================
# RUN EVALUATION
# ============================================================

for i, item in enumerate(
    golden_dataset,
    start=1
):

    print(
        f"\nRunning evaluation "
        f"{i}/{len(golden_dataset)}"
    )

    query = item["query"]

    thread_id = f"eval-{i}"


    # ========================================================
    # RUN AGENT
    # ========================================================

    result = run_agent_for_eval(
        query,
        thread_id
    )

    response = result.get(
        "response",
        ""
    )

    products = result.get(
        "eligible_products",
        []
    )


    # ========================================================
    # LANGFUSE EVALUATION OBSERVATION
    # ========================================================

    with langfuse.start_as_current_observation(
        as_type="span",
        name="evaluation",
        input={
            "query": query,
            "evaluation_id": i,
            "thread_id": thread_id
        }
    )   as span:


        # ====================================================
        # CORRECTNESS
        # ====================================================

        correctness = evaluate_correctness(
            query,
            response,
            item["expected_category"],
            item["expected_max_budget"]
        )

        correctness_scores.append(
            correctness
        )


        # ====================================================
        # RELEVANCE
        # ====================================================

        relevance = evaluate_relevance(
            query,
            response
        )

        relevance_scores.append(
            relevance
        )


        # ====================================================
        # HALLUCINATION
        # ====================================================

        hallucination = evaluate_hallucination(
            response
        )

        hallucination_scores.append(
            hallucination
        )


        # ====================================================
        # GROUNDEDNESS
        # ====================================================

        groundedness = evaluate_groundedness(
            response,
            products
        )

        groundedness_scores.append(
            groundedness
        )


        # ====================================================
        # STORE EVALUATION OUTPUT
        # ====================================================

        span.update(
            output={
                "response": response,
                "correctness": correctness,
                "relevance": relevance,
                "hallucination": hallucination,
                "groundedness": groundedness
            }
        )


        # ====================================================
        # LANGFUSE SCORES
        # ====================================================

        span.score(
            name="correctness",
            value=correctness
        )

        span.score(
            name="relevance",
            value=relevance
        )

        span.score(
            name="hallucination",
            value=hallucination
        )

        span.score(
            name="groundedness",
            value=groundedness
        )


    # ========================================================
    # TERMINAL OUTPUT
    # ========================================================

    print(
        "Correctness:",
        correctness
    )

    print(
        "Relevance:",
        relevance
    )

    print(
        "Hallucination:",
        hallucination
    )

    print(
        "Groundedness:",
        groundedness
    )


# ============================================================
# FLUSH LANGFUSE
# ============================================================

langfuse.flush()


# ============================================================
# AVERAGE SCORES
# ============================================================

print("\n" + "=" * 50)
print("FINAL EVALUATION RESULTS")
print("=" * 50)

print(
    "Average Correctness:",
    sum(correctness_scores)
    / len(correctness_scores)
)

print(
    "Average Relevance:",
    sum(relevance_scores)
    / len(relevance_scores)
)

print(
    "Average Hallucination:",
    sum(hallucination_scores)
    / len(hallucination_scores)
)

print(
    "Average Groundedness:",
    sum(groundedness_scores)
    / len(groundedness_scores)
)

