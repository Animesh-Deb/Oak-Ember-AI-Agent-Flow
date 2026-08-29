def product_to_text(row):

    return f"""
Product ID: {row['product_id']}
Name: {row['name']}
Category: {row['category']}
Price: {row['price']}
Description: {row['description']}
Features: {row['features']}
Ideal For: {row['ideal_for']}
Limitations: {row['limitations']}
Product URL: {row['product_url']}
Active: {row['active']}
"""