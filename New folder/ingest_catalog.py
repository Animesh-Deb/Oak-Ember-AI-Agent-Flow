from pathlib import Path

import pandas as pd

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from aichains import llm
import config
import AIretrieval
from utils import product_to_text


# =========================================================
# PATHS
# =========================================================
from pathlib import Path
BASE_DIR = Path.cwd() 
DATA_DIR = BASE_DIR / "data" 

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

CATALOG_PATH = DATA_DIR / "products.csv"

CHROMA_PATH = DATA_DIR / "chroma_db"


# =========================================================
# LOAD PRODUCT CATALOG
# =========================================================

products_df = pd.read_csv(CATALOG_PATH)

print("Products loaded:", len(products_df))



# =========================================================
# CREATE DOCUMENTS
# =========================================================

documents = []
ids = []

for _, row in products_df.iterrows():

    document = Document(
        page_content=product_to_text(row),
        metadata={
            "product_id": row["product_id"],
            "category": row["category"],
            "price": row["price"],
            "active": row["active"]
        }
    )

    documents.append(document)

    ids.append(
        str(row["product_id"])
    )


print("Documents created:", len(documents))


# =========================================================
# EMBEDDINGS
# =========================================================

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


# =========================================================
# CREATE CHROMA
# =========================================================

vectorstore = Chroma.from_documents(

    documents=documents,

    embedding=embeddings,

    ids=ids,

    collection_name="oak_ember_products",

    persist_directory=str(CHROMA_PATH)
)


# =========================================================
# VERIFY
# =========================================================

print(
    "Chroma vectors:",
    vectorstore._collection.count()
)

print("\nCatalog ingestion completed successfully.")