import streamlit as st

# Streamlit interface
@st.cache
def index():
    st.title("CPMI Application Management")

    # Add a new application
    with st.form("add_application"):
        name = st.text_input("Application Name")
        scoped_year = st.number_input("Scoped Year")
        product_owner = st.text_input("Product Owner")

        submitted = st.form_submit_button("Add Application")

        if submitted:
            st.success(f"Application added successfully! Name: {name}, Scoped Year: {scoped_year}, Product Owner: {product_owner}")

# Run the Streamlit app
if __name__ == "__main__":
    index()
