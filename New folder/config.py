from dotenv import load_dotenv
import os 
load_dotenv() 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY") 
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY") 
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST") 