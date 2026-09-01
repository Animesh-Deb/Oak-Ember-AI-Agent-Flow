import json 
import uuid 
import re 
import sqlite3 
import warnings 
from datetime import datetime, timedelta 
import pandas as pd 
import numpy as np 
from dotenv import load_dotenv 
from pydantic import BaseModel, Field 
warnings.filterwarnings("ignore")
from langgraph.graph.message import add_messages 
from typing import Annotated, Literal, TypedDict

# PYDANTIC STATE -  Customer needs 
class CustomerNeeds(BaseModel): 
    category: str | None = None 
    use_case: str | None = None 
    budget: float | None = None 
    required_features: list[str] = Field(default_factory=list) 
    preferences: list[str] = Field(default_factory=list) 
    constraints: list[str] = Field(default_factory=list)
# default_factory=list means: if no value is provided, create a new empty list [] for this field.

#Intent 
class IntentResult(BaseModel):
    intent: Literal[
        "product_enquiry",
        "unsubscribe",
        "other"
    ]
    confidence: float
    
#Recommendation 
class ProductRecommendation(BaseModel): 
    product_id: str 
    reason: str 
    price: float
    tradeoff: str | None = None
    
#Final response 
class RecommendationResponse(BaseModel): 
    summary: str 
    recommendations: list[ProductRecommendation] 
    clarification_question: str | None = None 
    assumptions: list[str] = Field(default_factory=list) 


#Define Sales State 

class SalesState(TypedDict, total=False): 
 
    # Conversation 
    query: str 
    source: str
    thread_id: str 
    name: str
    email: str
    contact: str
    messages: Annotated[ 
        list, 
        add_messages 
    ] 
 
    # Guardrails 
    guardrail_result: dict 
 
    # Intent 
    intent: str 
    intent_confidence: float 
 
    # Customer requirements 
    needs: CustomerNeeds 
 
    # Clarification 
    clarification_count: int 
    clarification_question: str 
 
    # Retrieval 
    retrieved_products: list[dict] 
 
    # Filtering / ranking 
    eligible_products: list[dict] 
 
    # Recommendation 
    recommendation: dict 
 
    # Validation 
    validation_result: dict 
 
    # Final response 
    response: str 
 
    # Error 
    error: str
    
class CustomerEnquiry(BaseModel):

    name: str = ""
    email: str = ""
    contact: str = ""
    category: str = ""
    budget: str = ""