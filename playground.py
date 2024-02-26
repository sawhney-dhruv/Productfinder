import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import openai

# Set your OpenAI API key here
openai.api_key = 'openai key here'

def show_image_from_url(url):
    """Display an image from a given URL."""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

url = "https://fakestoreapi.com/products"
response = requests.get(url)
filtered_products = []
product_cat = set()
descriptions = set()
if response.status_code == 200:
        all_products = response.json()
for product in all_products:
    category = product['title'].lower()
    product_cat.add(category)
    description1 = product['description'].lower()
    descriptions.add(description1)
# for product in all_products:
#     description1 = product['description'].lower()
#     descriptions.add(description1)



def preprocess_query_with_gpt(query):
    try:
        # Use OpenAI API to process the query
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model to use
            messages=[
                {"role": "system", "content": f"Given the user query {query}: identify the product only from \n\n" + "\n".join(product_cat) + "using the product description found in \n\n"  + "\n".join(descriptions) + "Format your response as: product_name only. output should match from" + "\n".join(product_cat) + "\n" + "Output can have multiple product names but only from the product list \n "},  # System prompt
               # {"role": "system", "content": f"Given the user query {query}: identify the product category only from \n\n" + "\n".join(products) + "Please provide only the product name from the list and include any mentioned specific attributes (e.g., color). Format your response as: Product Category, Specific Attributes"},  # System prompt
               
                #{"role": "system", "content": "Given the user query '{query}', identify the product category only from"+.join(products)+"recommendation"},  # System prompt
                {"role": "user", "content": query}  # User query
            ]
        )
        ai_response = response['choices'][0]['message']['content'].strip()  # Extract and strip the AI response
        return ai_response  # Return the processed query
    except Exception as e:
        st.error(f"An error occurred: {e}")  # Display error message in the Streamlit app
        return query  # Return the original query in case of an error

def fetch_products(product_type):
    """
    Fetch products based on type and optional attributes with improved matching logic.
    """
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
    filtered_products = []
    matches = set()

    if response.status_code == 200:
        all_products = response.json()
        a=set(product_type)
        set_a_value_lower = next(iter(a)).lower()
        b =set(list(product_cat))
        for a_value in a:
            a_value_lower = a_value.lower()  # Convert to lowercase for case-insensitive comparison
            for b_value in b:
                if a_value_lower in b_value.lower():
                    matches.add(b_value)
        for product in all_products:
            title = product['title'].lower()  # Convert title to lowercase for case-insensitive comparison
            if title in matches:
                filtered_products.append(product)
    else:
        print(f"Error fetching products: {response.status_code}")

# After the loop, check if filtered_products is populated
    if matches:
        print(f"Found {len(matches)} matching products.")
    else:
        print("No products matched.")
    return filtered_products

def main():
    """Run the Streamlit app for product finder chatbot."""
    st.title('Product Finder Chatbot')

    user_query = st.text_input('Ask me for a product (e.g., "show only bags", "show only t-shirts with blue color"):', '')

    if st.button('Clear Conversation'):
        st.experimental_rerun()

    if user_query:
        # Process the query through GPT-3 
        ai_response = preprocess_query_with_gpt(user_query)
        #print(ai_response)
        #print(ai_response.split(",")[0])
        # Simplified parsing of GPT-3 response; in practice, parse this response to extract structured data
        product_type = [value.strip() for string in ai_response.split("\n") for value in string.split(',')]
     #   print(product_type)
        #attributes = ai_response.split(",")[0:] if "," in ai_response else None

        products = fetch_products(product_type)
        #print(attributes)
        #print(products)


        if products:
            for product in products:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        img = show_image_from_url(product['image'])
                        st.image(img, caption=product['title'])
                    with col2:
                        st.write(f"**{product['title']}**")
                        st.write(f"Price: ${product['price']}")
                        st.write(f"Description: {product['description']}")
        else:
            st.write("No products found matching your query.")

if __name__ == "__main__":
    main()
