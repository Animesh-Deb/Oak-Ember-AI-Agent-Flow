from langchain_openai import ChatOpenAI
from typer import prompt 
from graph import sales_graph 
 
judge_llm = ChatOpenAI( 
    model="gpt-4o-mini", 
    temperature=0 
) 
 
 
def evaluate_correctness( 
    query, 
    response, 
    expected_category, 
    expected_max_budget 
): 
 
    prompt = f""" 
    Evaluate whether the AI response correctly answers 
    the customer's furniture request. 
    Customer query: 
    {query} 
    Expected category: 
    {expected_category} 
    Expected maximum budget: 
    {expected_max_budget} 
    AI response: 
    {response} 
    Give a score from 0 to 1. 
    1 = completely correct 
    0 = completely incorrect 
    Return ONLY the number. 
    """ 
    result = judge_llm.invoke(prompt) 
    return float(result.content.strip())
 
def evaluate_relevance( 
query, 
response 
): 
    prompt = f""" 
    Evaluate how relevant the AI response is to the 
    customer's furniture request. 
    Customer query: 
    {query} 
    AI response: 
    {response} 
    Score from 0 to 1. 
    1 = completely relevant 
    0 = irrelevant 
    Return ONLY the number. 
    """ 
    result = judge_llm.invoke(prompt) 
    return float(result.content.strip()) 

def evaluate_hallucination( 
response 
): 
    prompt = f""" 
    Determine whether the following AI response contains 
    invented product information. 
    AI response: 
    {response} 
    Score: 
    1 = no hallucination 
    0 = hallucinated information 
    Return ONLY the number. 
    """ 
    result = judge_llm.invoke(prompt) 
    return float(result.content.strip()) 

def evaluate_groundedness( 
response, 
products 
): 
    prompt = f""" 
    Determine whether the AI response is grounded in the 
    provided product catalog. 
    Product catalog: 
    {products} 
    AI response: 
    {response} 
    Score from 0 to 1. 
    1 = fully grounded 
    0 = not grounded 
    Return ONLY the number. 
    """ 
    result = judge_llm.invoke(prompt) 
    return float(result.content.strip()) 

def run_agent_for_eval(query, thread_id): 
 
    return sales_graph.invoke( 
        { 
            "query": query 
        }, 
        config={ 
            "configurable": { 
                "thread_id": thread_id 
            } 
        } 
    )