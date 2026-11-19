import streamlit as st

st.title("EYARC Demo")

st.write("Welcome to my Streamlit app.")

name = st.text_input("What's your name?")

if st.button("Submit"):
    st.success(f"Hello, {name}!")