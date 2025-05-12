# Import packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title and intro
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input name
name_on_order = st.text_input("Name on Smoothie")
if name_on_order:
    st.write("The name on your smoothie will be", name_on_order)

# Try to connect to Snowflake and fetch fruit options
try:
    # Connect to Snowflake using st.connection
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Get FRUIT_NAME and SEARCH_ON from fruit_options table
    fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
    fruit_data = fruit_df.collect()

    # Create a list of fruit names for display and a map to SEARCH_ON
    fruit_names = [row['FRUIT_NAME'] for row in fruit_data]
    search_map = {row['FRUIT_NAME']: row['SEARCH_ON'] for row in fruit_data}

    # Show fruit data in a dataframe for reference (can remove later)
    st.dataframe(fruit_df.to_pandas(), use_container_width=True)

    # Let user select ingredients
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_names,
        max_selections=5
    )

    # Insert order if name and ingredients are provided
    if ingredients_list and name_on_order:
        ingredients_string = ', '.join(ingredients_list)
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        st.write("Here's your insert statement:")
        st.code(my_insert_stmt, language='sql')

        if st.button('Submit Order'):
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")

    # Show nutrition info using API
    if ingredients_list:
        for fruit in ingredients_list:
            search_term = search_map.get(fruit, fruit).lower().replace(' ', '%20')
            api_url = f"https://my.smoothiefroot.com/api/fruit/{search_term}"
            response = requests.get(api_url)

            st.subheader(f"{fruit} Nutrition Information")

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.warning(f"No data found for {fruit} (searched for '{search_term}')")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.warning("Please ensure you have a valid Snowflake connection and available warehouse credits.")

# Catch missing name input if submit clicked
if not name_on_order and st.button('Submit Order'):
    st.warning("Please enter your name before placing an order.")
