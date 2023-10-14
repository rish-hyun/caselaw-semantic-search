import streamlit as st
from search import es_client


st.title("Case Law Semantic Search Engine")
st.subheader("Search for similar cases using semantic search")
st.write(
    "This is a demo of a semantic search engine for case law. It uses a pre-trained sentence transformer model to embed cases into a vector space. The vector space is then indexed using Elasticsearch. The search is performed by embedding the query and finding the nearest neighbors in the vector space. The results are then retrieved from Elasticsearch."
)

st.subheader("How to use")
st.write(
    "Enter a query in the search box below. The search engine will return the most similar cases to the query."
)

st.subheader("How it works")
st.write(
    "The search engine uses a pre-trained sentence transformer model to embed cases into a vector space. The vector space is then indexed using Elasticsearch. The search is performed by embedding the query and finding the nearest neighbors in the vector space. The results are then retrieved from Elasticsearch."
)


st.subheader("Search")
query = st.text_input("Enter a query")
if query:
    results = es_client.search(query)
    for result in results:
        st.write(result)
