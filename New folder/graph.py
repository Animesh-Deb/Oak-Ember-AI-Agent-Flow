from langgraph.graph import ( 
    StateGraph, 
    START, 
    END 
) 
 
from langgraph.checkpoint.memory import MemorySaver 
 
from state import SalesState 
from sales_nodes import (
    customer_enquiry_node,
    store_enquiry_node
)
from guaradrail_nodes import ( 
    guardrail_node 
) 


memory = MemorySaver()
 
from sales_nodes import ( 
    intent_node, 
    needs_node, 
    needs_validation_node, 
    clarification_node, 
    insufficient_response_node, 
    retrieval_node, 
    filtering_node, 
    ranking_node, 
    route_after_needs_validation 
) 
 
from recommendation_nodes import ( 
    recommendation_node, 
    recommendation_validation_node 
) 
 
from response_nodes import ( 
    response_node, 
    blocked_response_node, 
    no_match_response_node, 
    unsubscribed_response_node, 
    greetings_response_node
) 

# CONDITIONAL ROUTING    
# Guardrail routing 
def route_after_guardrail( 
    state: SalesState 
): 
 
    result = state["guardrail_result"] 
 
    if not result["allowed"]: 
        return "blocked" 
 
    return "allowed"

# Intent routing 
def route_after_intent( 
    state: SalesState 
): 
 
    intent = state.get("intent") 
 
    if intent == "product_enquiry": 
        return "product" 
 
    if intent == "unsubscribe": 
        return "unsubscribe" 
  
    if intent == "only greetings": 
            return "greetings"
        
    if intent == "greetings with product enquiry": 
        return "product"
    return "other"

# Product availability routing in case there are no products matching the customer's requirements

def route_after_filter( 
    state: SalesState 
): 
 
    products = state.get( 
        "eligible_products", 
        [] 
    ) 
 
    if not products: 
        return "no_match" 
 
    return "match"

# Create graph 
builder = StateGraph(SalesState)

#Adding nodes 
# Input guardrail
builder.add_node(
    "guardrail",
    guardrail_node
)

# Intent classification
builder.add_node(
    "intent",
    intent_node
)

# Customer needs extraction
builder.add_node(
    "needs",
    needs_node
)

builder.add_node( 
    "needs_validation", 
    needs_validation_node 
)

builder.add_node( 
    "clarification", 
    clarification_node 
)
builder.add_node(
    "customer_enquiry",
    customer_enquiry_node
)
builder.add_node(
    "insufficient",
    insufficient_response_node
)

# Product retrieval
builder.add_node(
    "retrieval",
    retrieval_node
)

# Product filtering
builder.add_node(
    "filter",
    filtering_node
)
builder.add_node(
    "store_enquiry",
    store_enquiry_node
)


# Product ranking
builder.add_node(
    "ranking",
    ranking_node
)

# LLM recommendation generation
builder.add_node(
    "recommendation",
    recommendation_node
)

# Recommendation validation / grounding
builder.add_node(
    "validation",
    recommendation_validation_node
)

# Final response
builder.add_node(
    "response",
    response_node
)
builder.add_node(
    "blocked_response",
    blocked_response_node
)

builder.add_node(
    "greetings_response",
    greetings_response_node
)

builder.add_node(
    "no_match_response",
    no_match_response_node
)

builder.add_node(
    "unsubscribe_response",
    unsubscribed_response_node
)
builder.add_node(
    "other_response",
    blocked_response_node
    
)

#Connecting the graph 

# START → Guardrail
builder.add_edge(
    START,
    "guardrail"
)


# ============================================================
# GUARDRAIL ROUTING
# ============================================================

builder.add_conditional_edges(
    "guardrail",
    route_after_guardrail,
    {
        "allowed": "intent",
        "blocked":  "blocked_response"
    }
)
builder.add_edge(
    "blocked_response",
    END )

# ============================================================
# INTENT ROUTING
# ============================================================

builder.add_conditional_edges(
    "intent",
    route_after_intent,
    {
        "product": "needs",
        "unsubscribe": "unsubscribe_response",
        "other": "other_response",
        "greetings": "greetings_response"
    }
)


# ============================================================
# NEEDS → RETRIEVAL
# ============================================================

builder.add_edge(
    "needs",
    "needs_validation"
)
# ============================================================
# NEEDS VALIDATION ROUTING
# ============================================================

builder.add_conditional_edges(
    "needs_validation",
    route_after_needs_validation,
    {
        "clarify": "clarification",
        "insufficient": "insufficient",
        "ready": "retrieval"
    }
)

# ============================================================
# CLARIFICATION → END
# ============================================================

builder.add_edge(
    "clarification",
    END
)


# ============================================================
# INSUFFICIENT → END
# ============================================================

builder.add_edge(
    "insufficient",
    END
)


# ============================================================
# RETRIEVAL → FILTER
# ============================================================

builder.add_edge(
    "retrieval",
    "filter"
)


# ============================================================
# FILTER ROUTING
# ============================================================

builder.add_conditional_edges(
    "filter",
    route_after_filter,
    {
        "match": "ranking",
        "no_match": "no_match_response"
    }
)


# ============================================================
# RANKING → RECOMMENDATION
# ============================================================

builder.add_edge(
    "ranking",
    "recommendation"
)


# ============================================================
# RECOMMENDATION → VALIDATION
# ============================================================

builder.add_edge(
    "recommendation",
    "validation"
)

builder.add_edge(
    "validation",
    "customer_enquiry"
)
builder.add_edge(
    "customer_enquiry",
    "store_enquiry"
)
# ============================================================
# VALIDATION → RESPONSE
# ============================================================

builder.add_edge(
    "store_enquiry",
    "response"
)


# ============================================================
# RESPONSE → END
# ============================================================

builder.add_edge(
    "response",
    END
)

builder.add_edge(
    "no_match_response",
    END)

builder.add_edge(
    "unsubscribe_response",
    END
)
builder.add_edge(
    "other_response",
    END
)

# Compile graph 
sales_graph = builder.compile(checkpointer=memory ) 

