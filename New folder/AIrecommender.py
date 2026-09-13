from langchain_openai import ChatOpenAI 
 
from state import RecommendationResponse 
import state
from utils import product_to_text
from aichains import llm
import pandas as pd
from langfuse_config import langfuse
from langfuse import get_client

langfuse = get_client()
#The specification proposes: 
#Semantic similarity     50% 
#Feature match           30% 
#Budget closeness        20% 

recommendation_llm = ChatOpenAI( 
    model="gpt-4o-mini", 
    temperature=0 
).with_structured_output( 
    RecommendationResponse 
) 

 
def calculate_budget_score( 
    price, 
    budget ): 
 
    if budget is None: 
        return 1.0 
 
    difference = abs(budget - price) 
 
    return max( 
        0, 
        1 - difference / budget 
    )
    
# Ranking 
def rank_products( 
    products, 
    needs ): 
 
    products = products.copy() 
 
    products["budget_score"] = products["price"].apply( 
        lambda price: calculate_budget_score( 
            price, 
            needs.budget 
        ) 
    ) 
 
    products["final_score"] = ( 
        products["budget_score"] * 0.20 
    ) 
 
    return products.sort_values( 
        "final_score", 
        ascending=False 
    ) 

# RECOMMENDATION GENERATION 
# Now the LLM finally enters the recommendation decision as an explanation layer. 
 

recommendation_llm = llm.with_structured_output( 
    RecommendationResponse 
)

def generate_recommendation(
    customer_message,
    needs,
    eligible_products
    ):

    product_context = "\n\n".join(
        product_to_text(row)
        for _, row in eligible_products.iterrows()
    )

    prompt = f"""
    You are a sales assistant for Oak & Ember Interiors.

    Recommend products ONLY from the eligible products provided.

    Customer request:
    {customer_message}

    Customer needs:
    {needs.model_dump_json()}

    Eligible products:
    {product_context}

    IMPORTANT RESPONSE FORMAT:

You must generate a summary and product recommendations.

    SUMMARY RULES:

    - The summary MUST begin with a greeting.
    - Start the summary with:
    "Hello, thank you for your interest in Oak & Ember Interiors."
    - Acknowledge the customer's furniture request.
    - Do not use exaggerated words such as "great", "perfect", or "best".
    - Keep the summary concise.
    
    Example summary:

    "Hello, thank you for your interest in Oak & Ember Interiors.
    Based on your request for office storage, here are the available options."
    
    For each recommendation:
    - Use the exact product ID from the eligible products.
    - Use the EXACT price from the eligible products.
    - Provide the price even if the customer did not explicitly ask for it.
    - Explain why it fits.
    - Mention an honest trade-off.
    - Do not invent product information.
    - Do not change prices.
    - Do not invent features.

    Return a structured recommendation.

    If the customer asks specifically for price, make sure the price is explicitly included.
    """

    with langfuse.start_as_current_observation(
        as_type="generation",
        name="generate_recommendation",
        model="gpt-4o-mini",
        input=prompt
    ) as generation:

        result = recommendation_llm.invoke(prompt)

        generation.update(
            output=result.summary
        )

    langfuse.flush()

    return result

#OUTPUT VALIDATION
 
def validate_recommendation( 
    recommendation, 
    eligible_products ): 
 
    valid_ids = set( 
        eligible_products["product_id"] 
    ) 
 
    for item in recommendation.recommendations: 
 
        if item.product_id not in valid_ids: 
            return False,
    return True


    
