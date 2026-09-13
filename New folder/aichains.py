from langchain_openai import ChatOpenAI
import langfuse 
from state import ( CustomerNeeds, IntentResult)
import config
from langfuse import get_client

langfuse = get_client()
llm = ChatOpenAI( 
    model="gpt-4o-mini", 
    temperature=0 ) 

#INTENT CLASSIFICATION 

from typing import Literal
IntentResult.model_rebuild()
intent_llm = llm.with_structured_output( 
    IntentResult    ) 

def classify_intent(message): 
    prompt = f""" 
    Classify the customer message. 
    Possible intents: product_enquiry - unsubscribe - other - only greetings-
    greetings with product enquiry
    Customer message: 
    {message} 
     """ 
    with langfuse.start_as_current_observation(
    as_type="generation",
    name="intent-classification",
    model="gpt-4o-mini",
    input=prompt
)   as generation:

        result = llm.invoke(prompt)

        generation.update(
        output=result.content
    )
 
    langfuse.flush()  
    return intent_llm.invoke(prompt)

#NEEDS EXTRACTION 
 
needs_llm = llm.with_structured_output( 
CustomerNeeds) 

def extract_customer_needs(
    message,
    previous_needs=None
):

    previous_context = ""

    if previous_needs:
        previous_context = f"""
        Previously identified customer needs:
        {previous_needs.model_dump_json()}
        """

    prompt = f"""
    Extract and update the customer's furniture requirements.

    Identify:
    - category
    - use case
    - budget
    - required features
    - preferences
    - constraints
    
    IMPORTANT CATEGORY RULE:

    The "category" must be the specific furniture/product type
    the customer is asking for.

    Examples:

    "office chair" → category = "Office Chair"
    "office desk" → category = "Office Desk"
    "dining table" → category = "Dining Table"
    "Storage" → category = "Storage"
    "Bench" → category = "Bench"

    Do NOT use broad categories such as:
    "furniture", "office", "home", "seating", etc.

    For example:

    Customer: "office chair under 50000"

    Return:
    category = "Office Chair"
    use_case = "office"
    budget = 50000

    Rules:
    - Preserve previously identified requirements.
    - Add new requirements from the current message.
    - If the customer explicitly changes a requirement,
      update the old requirement.
    - Do not invent information.
    - Do not remove an existing requirement unless the
      customer explicitly changes or removes it.

    {previous_context}

    Current customer message:
    {message}
    """
    with langfuse.start_as_current_observation(
        as_type="generation",
        name="needs-extraction",
        model="gpt-4o-mini",
        input=prompt
    ) as generation:

        result = llm.invoke(prompt) 
 
        generation.update( 
            output=result.content 
    ) 
 
    langfuse.flush() 
    return needs_llm.invoke(prompt)

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