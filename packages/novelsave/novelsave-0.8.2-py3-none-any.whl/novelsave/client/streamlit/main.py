import streamlit as st

st.title("novelsave")

url_disabled = False
url = st.text_input('Enter novel url here', disabled=url_disabled)