from state import SalesState 

def insufficient_response_node(state: SalesState):

    return {
        "response": "I don't have enough information to find a suitable product."
    }
    
# Final response node 

def response_node(state: SalesState):

    recommendation = state["recommendation"]

    lines = []

    # Summary
    lines.append(
        recommendation["summary"]
    )

    lines.append("")

    # Recommendations
    for item in recommendation["recommendations"]:

        lines.append(
            f"### {item['product_id']}"
        )

        lines.append(
            f"- **Why it fits:** {item['reason']}"
        )

        if item.get("price"):
            lines.append(
                f"- **Price:** ₹{item['price']}"
            )

        if item.get("tradeoff"):
            lines.append(
                f"- **Trade-off:** {item['tradeoff']}"
            )

        lines.append("")

    # Closing message
    lines.append(
        "Thank you for choosing **Oak & Ember Interiors**!"
    )

    return {
        "response": "\n".join(lines)
    }
    
#Blocked Response Node for Guardrail Violations or Unmatched Products
def blocked_response_node(state: SalesState):

    return {
        "response": (
            "I'm sorry, but I can't help with that request. "
            "I can help you find furniture from Oak & Ember Interiors."
            
        )
    }
    
def unsubscribed_response_node(state: SalesState):

    return {
        "response": (
            "I'm sorry for your inconvenience."
            "To request unsubscribing from our emails, please visit our website or contact support."
        )
    }
    
#No Match Response Node for Unmatched Products
def no_match_response_node(state: SalesState):

    return {
        "response": (
            "I couldn't find a product that matches a combination of all of your "
            "requirements. Could you please help to provide just the furniture category to see all the options available ? "
            "I can then help you find something that fits your needs."
        )
    }
    
def greetings_response_node(state: SalesState):

    return {
        "response": (
            "Hello! How can I assist you today? If you provide me your " 
            "furniture category, budget and/or features, I can help you find the perfect piece"
            " from Oak & Ember Interiors."
        )
    }
            