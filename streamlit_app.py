# Import Python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: name on order
name_on_order = st.text_input("Name on Smoothie")
if name_on_order:
    st.write("The name on your smoothie will be", name_on_order)

# Connect to Snowflake
try:
    # Using Streamlit connection
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Query fruit data
    fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
    pd_df = fruit_df.to_pandas()

    # Get fruit names for selection
    fruit_names = pd_df["FRUIT_NAME"].tolist()

    # Let user select fruits
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_names,
        max_selections=5
    )

    # Insert order if fruits and name are selected
    if ingredients_list and name_on_order:
        ingredients_string = ' '.join(ingredients_list)
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        st.write("Here's your insert statement:")
        st.code(insert_stmt, language='sql')

        if st.button('Submit Order'):
            session.sql(insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")

    elif not name_on_order and st.button('Submit Order'):
        st.warning("Please enter your name before placing an order.")

    # Show nutrition info for selected fruits
    if ingredients_list:
        for fruit_chosen in ingredients_list:
            # Get SEARCH_ON value
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

            st.subheader(f"{fruit_chosen} Nutrition Information")
            try:
                response = requests.get(f"https://fruityvice.com/api/fruit/{search_on.lower()}")
                if response.status_code == 200:
                    fruity_data = response.json()
                    st.dataframe(data=pd.json_normalize(fruity_data), use_container_width=True)
                else:
                    st.warning(f"No nutrition info found for '{fruit_chosen}' (SEARCH_ON = '{search_on}').")
            except Exception as e:
                st.error(f"API error for {fruit_chosen}: {e}")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.warning("Please ensure you have the correct Snowflake connection configured.")


