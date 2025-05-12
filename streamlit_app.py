# Import packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: name on order
name_on_order = st.text_input("Name on Smoothie")
if name_on_order:
    st.write("The name on your smoothie will be", name_on_order)

# Connect to Snowflake
try:
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Load fruit options
    fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
    pd_df = fruit_df.to_pandas()

    # Display DataFrame for debugging (optional)
    # st.dataframe(pd_df, use_container_width=True)

    # Fruit selection input
    fruit_names = pd_df['FRUIT_NAME'].tolist()
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_names,
        max_selections=5
    )

    # Insert order into database
    if ingredients_list and name_on_order:
        ingredients_string = ' '.join(ingredients_list)
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        st.write("Here's your insert statement:")
        st.code(insert_stmt, language='sql')

        if st.button('Submit Order'):
            session.sql(insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")

    # Handle case where user clicks submit without entering name
    elif not name_on_order and st.button('Submit Order'):
        st.warning("Please enter your name before placing an order.")

    # Fetch and display nutritional info
    if ingredients_list:
        for fruit_chosen in ingredients_list:
            try:
                # Get search term for fruit
                search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
                st.write(f"The search value for {fruit_chosen} is '{search_on}'.")

                # Call the API
                api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
                response = requests.get(api_url)

                if response.status_code == 200:
                    st.subheader(f"{fruit_chosen} Nutrition Information")
                    st.dataframe(response.json(), use_container_width=True)
                else:
                    st.warning(f"No nutrition info found for {fruit_chosen} (searched for '{search_on}').")

            except Exception as e:
                st.error(f"Could not get data for {fruit_chosen}: {e}")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.warning("Please ensure your Snowflake connection is properly configured.")

