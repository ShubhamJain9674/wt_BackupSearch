import os  # To check file existence
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import sys
sys.stdout.reconfigure(encoding='utf-8')


def fetch_exact_product(keyword):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0 Safari/537.36"
    }

    url = f"https://www.amazon.in/s?k={keyword}"  # Amazon search URL with keyword
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to fetch products from Amazon"}

    soup = BeautifulSoup(response.text, 'html.parser')
    products = []

    # Extract product names and prices
    for product in soup.select('.s-result-item'):
        title = product.select_one('h2 a span')
        price = product.select_one('.a-price .a-offscreen')

        if title and price:
            try:
                # Convert price to float for accurate comparisons
                price_value = float(price.text.replace(',', '').replace('₹', '').strip())
                product_name = title.text.strip()

                # Check if the product name matches the keyword exactly
                if keyword.lower() in product_name.lower():  # Case insensitive match
                    products.append({"name": product_name, "price": price_value})
            except ValueError:
                continue

    if not products:
        return {"error": "No products found"}

    # Find the product with the lowest price
    lowest_price_product = min(products, key=lambda x: x["price"])

    # Insert the product into MongoDB
    insert_into_mongodb(lowest_price_product)

    return lowest_price_product

def insert_into_mongodb(product):
    try:
        # Connect to MongoDB (ensure MongoDB is running on localhost or set your URI)
        client = MongoClient("mongodb://localhost:27017/")
        db = client["price_scout"]  # Database name
        collection = db["products"]  # Collection name

        # Check if product already exists in the collection
        existing_product = collection.find_one({"name": product["name"]})

        if existing_product:
            # If the product exists, update it only if the new price is lower
            if existing_product["price"] > product["price"]:
                collection.update_one({"name": product["name"]}, {"$set": product})
                print(f"Updated the price of {product['name']} to ₹{product['price']}")
        else:
            # If the product doesn't exist, insert a new document
            collection.insert_one(product)
            print(f"Inserted {product['name']} with price ₹{product['price']} into MongoDB")

    except Exception as e:
        print(f"Error inserting into MongoDB: {e}")

def get_keyword_from_file(filename="keyword.txt"):
    # Check if the file exists
    if not os.path.exists(filename):
        # Create the file if it doesn't exist
        with open(filename, "w") as file:
            file.write("")  # Create an empty file
        print(f"File '{filename}' created. Please add a keyword to it.")
        return None

    # Read the keyword from the file
    with open(filename, "r") as file:
        keyword = file.readline().strip()

    if not keyword:
        print(f"No keyword found in '{filename}'. Please add a keyword.")
        return None

    return keyword

if __name__ == "__main__":
    keyword = get_keyword_from_file()

    if keyword:
        result = fetch_exact_product(keyword)

        if "error" in result:
            print(result["error"])
        else:
            print(f"Lowest price for '{keyword}':")
            print(f"Product Name: {result['name']}")
            print(f"Price: ₹{result['price']}")
