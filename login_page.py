import streamlit as st
import pandas as pd

def login_page(email, password):
    # Load the user credentials from the Excel file
    df = pd.read_excel("user_credentials.xlsx")
    
    # Check if the provided email and password match any record
    matching_record = df[(df['email'] == email) & (df['password'] == password)]
    
    if len(matching_record) > 0:
        return True              
    else:
        return False

def main():
    st.title("Login Page")
    
    # Sidebar
    st.sidebar.header("Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")
    
    if login_button:
        if login_page(email, password):
            st.success("Login successful!")
        else:
            st.error("Invalid email or password. Please try again.")

if __name__ == "__main__":
    main()
