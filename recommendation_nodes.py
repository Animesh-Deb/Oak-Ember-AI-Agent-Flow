import pandas as pd 
from state import SalesState 
 
from AIrecommender import ( 
    generate_recommendation 
)

# Recommendation node 


def recommendation_node(state: SalesState): 
 
    products = pd.DataFrame( 
        state["eligible_products"] 
    ) 
 
    top_products = products.head(3) 
 
    print("\n" + "=" * 60)
    print("RECOMMENDATION INPUT")
    print(top_products[["product_id", "category", "price"]])
    print("=" * 60)

    print(
        pd.DataFrame(state["eligible_products"])[
        ["product_id", "category", "price"]
    ]
)
    
    recommendation = generate_recommendation( 
        state["query"], 
        state["needs"], 
        top_products 
    ) 
 
    return { 
        "recommendation": recommendation.model_dump() 
    }
    
#Recommendation validation node as the output guardrail

def recommendation_validation_node( 
    state: SalesState 
): 
 
    recommendation = state["recommendation"] 
 
    eligible_ids = { 
        product["product_id"] 
        for product in state["eligible_products"] 
    } 
 
    for item in recommendation["recommendations"]: 
 
        if item["product_id"] not in eligible_ids: 
 
            return { 
                "error": ( 
                    f"Invalid product recommended: " 
                    f"{item['product_id']}" 
                ) 
            } 
 
    return {} 