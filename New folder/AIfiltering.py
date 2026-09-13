import pandas as pd

#Budget filter 
def filter_by_budget( 
    products, 
    budget ): 
 
    if budget is None: 
        return products 
 
    return products[ 
        products["price"] <= budget 
    ]

 #Active filter 
def filter_active_products(products): 
 
    return products[ 
        products["active"] == True 
    ]
    
# Feature filter 

def filter_by_features( 
    products, 
    required_features 
): 
 
    if not required_features: 
        return products 
 
    mask = pd.Series( 
        True, 
        index=products.index 
    ) 
 
    for feature in required_features: 
 
        mask &= products["features"].str.lower().str.contains( 
            feature.lower(), 
            na=False 
        ) 
 
    return products[mask] 

def filter_by_category(products, category):

    if not category:
        return products

    return products[
        products["category"].str.lower()
        == category.lower()
    ].copy()