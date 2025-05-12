# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input name
name_on_order = st.text_input("Name on Smoothie")
if name_on_order:
    st.write("The name on your smoothie will be", name_on_order)

# Connect to Snowflake and get the fruit names
try:
    cnx = st.connection("snowflake")
    session = cnx. session ()
    #session = get_active_session()
    fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
    fruit_names = [row['FRUIT_NAME'] for row in fruit_df.collect()]

    # Let user pick up to 5 fruits
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_names,
        max_selections=5
    )

    # Only build the insert if something is selected and name is given
    if ingredients_list and name_on_order:
        ingredients_string = ' '.join(ingredients_list)
        my_insert_stmt = f"""
            insert into smoothies.public.orders(ingredients, name_on_order)
            values ('{ingredients_string}', '{name_on_order}')
        """
        st.write("Here's your insert statement:")
        st.code(my_insert_stmt, language='sql')
        
        if st.button('Submit Order'):
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.warning("Please ensure you have the correct Snowflake connection configured.")

# Handle case where no name is provided
if not name_on_order and st.button('Submit Order'):
    st.warning("Please enter your name before placing an order.")


# New section to display smoothiefroot nutrition information
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response. json( ))
