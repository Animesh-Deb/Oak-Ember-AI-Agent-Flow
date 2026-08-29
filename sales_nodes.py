
import pandas as pd 
 
from state import SalesState 

from response_nodes import insufficient_response_node, response_node, blocked_response_node, unsubscribed_response_node, no_match_response_node
from langfuse_config import langfuse 
from langfuse import get_client

langfuse = get_client()

from aichains import ( 
    classify_intent, 
    extract_customer_needs, 
    needs_clarification, 
    generate_clarification_question 
) 
 
from AIretrieval import ( 
    retrieve_products, 
    documents_to_products 
) 
 
from AIfiltering import ( 
    filter_active_products, 
    filter_by_budget, 
    filter_by_features,
    filter_by_category
) 
 
from AIrecommender import ( 
    rank_products 
)

from state import CustomerNeeds
from aichains import llm

# Clarification question detection
def needs_clarification(needs: CustomerNeeds) -> bool: 
 
    # No category and no meaningful use case 
    if not needs.category and not needs.budget: 
        return True 
 
    return False

clarification_llm = llm

#Clarification question generation

def generate_clarification_question( 
query: str, 
needs: CustomerNeeds 
): 
    prompt = f""" 
    You are a furniture sales assistant for Oak & Ember Interiors. 
    The customer's request does not contain enough information 
    to confidently recommend products. 
    Customer request: 
    {query} 
 
    Extracted needs: 
    {needs.model_dump_json()} 
 
    Ask ONE concise clarification question. 
 
    Prioritize identifying the type/category of furniture required and budget of customer. 
 
    Do not recommend products yet. 
    Do not invent catalog information. 
    """ 
 
    result = clarification_llm.invoke(prompt) 
 
    return result.content

#Needs validation node, this node decides whether we can proceed
def needs_validation_node(state: SalesState): 
 
    needs = state["needs"] 
 
    if needs_clarification(needs): 
 
        return { 
            "clarification_question": 
                generate_clarification_question( 
                    state["query"], 
                    needs 
                ) 
        } 
 
    return { 
        "clarification_question": "" 
    } 
    
#  Clarification count
MAX_CLARIFICATIONS = 2 

# Clarification routing 
def route_after_needs_validation( 
    state: SalesState 
): 
 
    question = state.get( 
        "clarification_question", 
        "" 
    ) 
 
    clarification_count = state.get( 
        "clarification_count", 
        0 
    ) 
 
    if question and clarification_count < MAX_CLARIFICATIONS: 
 
        return "clarify" 
 
    if question and clarification_count >= MAX_CLARIFICATIONS: 
 
        return "insufficient" 
 
    return "ready" 

# Clarification node 
def clarification_node(state: SalesState): 
 
    current_count = state.get( 
        "clarification_count", 
        0 
    ) 
 
    return { 
        "clarification_count": current_count + 1, 
        "response": state[ 
        "clarification_question" 
] 
} 
    
#Intent node 
 
def intent_node(state: SalesState): 
 
    result = classify_intent( 
        state["query"] 
    ) 
    print("\n===== INTENT DEBUG =====")
    print("Query:", state["query"])
    print("Intent:", result.intent)
    print("Confidence:", result.confidence)
    print("========================\n")
    return { 
        "intent": result.intent, 
        "intent_confidence": result.confidence 
    }

#Needs node 
def needs_node(state: SalesState):

    print("\n\n******** NEEDS NODE EXECUTED ********")
    print("QUERY:", state.get("query"))

    current_message = state["query"]

    previous_needs = state.get("needs")

    updated_needs = extract_customer_needs(
        current_message,
        previous_needs
    )

    print("EXTRACTED NEEDS:")
    print(updated_needs.model_dump())

    print("************************************\n")

    return {
        "needs": updated_needs
    }
    
#Retrieval node 
def retrieval_node(state: SalesState): 
 
    documents = retrieve_products( 
        state["query"], 
        k=5 
    ) 
 
    products = documents_to_products( 
        documents 
    ) 
 
    return { 
        "retrieved_products": products.to_dict( 
            orient="records" 
        ) 
    } 
    
# Filtering node


def filtering_node(state: SalesState):

    products = pd.DataFrame(
        state["retrieved_products"]
    )

    needs = state["needs"]

    print("\n" + "=" * 60)
    print("FILTERING DEBUG")
    print("=" * 60)

    print("\nCustomer query:")
    print(state["query"])

    print("\nExtracted needs:")
    print(needs.model_dump())

    print("\nBEFORE FILTERING:")
    print(
        products[
            ["product_id", "category", "price"]
        ]
    )

    # Active filter
    products = filter_active_products(
        products
    )

    print("\nAFTER ACTIVE FILTER:")
    print(
        products[
            ["product_id", "category", "price"]
        ]
    )

    # Category filter
    products = filter_by_category(
        products,
        needs.category
    )

    print("\nAFTER CATEGORY FILTER:")
    print(
        products[
            ["product_id", "category", "price"]
        ]
    )

    # Budget filter
    products = filter_by_budget(
        products,
        needs.budget
    )

    print("\nAFTER BUDGET FILTER:")
    print(
        products[
            ["product_id", "category", "price"]
        ]
    )

    # Feature filter
    products = filter_by_features(
        products,
        needs.required_features
    )

    print("\nAFTER FEATURE FILTER:")
    print(
        products[
            ["product_id", "category", "price"]
        ]
    )

    # Langfuse tracing
    with langfuse.start_as_current_observation(
        as_type="span",
        name="product-filtering",
        input={
            "query": state["query"],
            "category": needs.category,
            "budget": needs.budget,
            "required_features": needs.required_features
        }
    ) as span:

        span.update(
            output={
                "eligible_product_ids":
                    products["product_id"].tolist(),
                "eligible_count":
                    len(products)
            }
        )

    langfuse.flush()

    print("=" * 60)

    return {
        "eligible_products": products.to_dict(
            orient="records"
        )
    }
    
# Ranking node


def ranking_node(state: SalesState):

    products = pd.DataFrame(
        state["eligible_products"]
    )

    needs = state["needs"]

    print("\n" + "=" * 60)
    print("RANKING DEBUG")
    print("=" * 60)

    print("\nBEFORE RANKING:")
    print(
        products[
            ["product_id", "category", "price"]
        ]
    )

    ranked = rank_products(
        products,
        needs
    )

    print("\nAFTER RANKING:")
    print(
        ranked[
            ["product_id", "category", "price"]
        ]
    )

    # Langfuse tracing
    with langfuse.start_as_current_observation(
        as_type="span",
        name="product-ranking",
        input={
            "product_ids":
                products["product_id"].tolist()
        }
    ) as span:

        span.update(
            output={
                "ranked_product_ids":
                    ranked["product_id"].tolist()
            }
        )

    langfuse.flush()

    print("=" * 60)

    return {
        "eligible_products": ranked.to_dict(
            orient="records"
        )
    }




    
