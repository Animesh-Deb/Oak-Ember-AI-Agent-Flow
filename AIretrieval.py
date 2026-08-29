from pathlib import Path
import trace

import pandas as pd

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import config
from langfuse_config import langfuse
from langfuse import get_client 
langfuse = get_client()


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

CHROMA_PATH = DATA_DIR / "chroma_db"


# =========================================================
# LOAD PRODUCT CATALOG
# =========================================================

products_df = pd.read_csv(
    DATA_DIR / "products.csv"
)


# =========================================================
# EMBEDDINGS
# =========================================================

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=config.OPENAI_API_KEY
)


# =========================================================
# LOAD EXISTING CHROMA
# =========================================================

vectorstore = Chroma(
    collection_name="oak_ember_products",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_PATH)
)


# =========================================================
# RETRIEVAL
# =========================================================


def retrieve_products(
    query,
    k=5
):

    with langfuse.start_as_current_observation(
        as_type="span",
        name="product-retrieval",
        input={
            "query": query,
            "k": k
        }
    ) as span:

        # Perform retrieval first
        results = vectorstore.similarity_search(
            query,
            k=k
        )

        # Trace retrieval output
        span.update(
            output={
                "retrieved_product_ids": [
                    doc.metadata.get("product_id")
                    for doc in results
                ],
                "retrieved_count": len(results)
            }
        )

    return results



# =========================================================
# DOCUMENTS → PRODUCTS
# =========================================================

def documents_to_products(documents):

    product_ids = [
        doc.metadata["product_id"]
        for doc in documents
    ]

    return products_df[
        products_df["product_id"].isin(product_ids)
    ].copy()
    
if __name__ == "__main__":

    results = retrieve_products(
        "office chair under budget 50000",
        k=5
    )

    print(
        "Retrieved:",
        len(results)
    )

    for doc in results:

        print(
            doc.metadata.get("product_id"),
            "|",
            doc.metadata.get("category"),
            "|",
            doc.metadata.get("price")
        )