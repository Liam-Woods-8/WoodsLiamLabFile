import streamlit as st

lab1_page = st.Page("lab1.py", title="lab 1")
lab2_page = st.Page("lab2.py", title="lab 2")

pg = st.navigation([lab2_page, lab1_page])

pg.run()