import streamlit as st
from search import es_client


st.title("Case Law Semantic Search Engine")
st.subheader("Search for similar cases using semantic search")

st.subheader("How to use")
st.write("Enter a query in the search box below. The search engine will return the most similar cases to the query.")

st.subheader("Search")
query = st.text_input("Enter a query")
if query:
    results = es_client.search(query)
    for result in results:
        st.write(result)
