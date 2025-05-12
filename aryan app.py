import streamlit as st
from pyvis.network import Network
import tempfile
import os
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import spacy
import networkx as nx
import streamlit.components.v1 as components

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

st.set_page_config(page_title="Knowledge Graph Generator", layout="wide")

st.title("📚 Knowledge Graph Generator from PDF / URL / Text")

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# Function to extract text from URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error for bad HTTP status codes
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching URL: {e}")
        return ""

# Function to generate graph from text
def generate_knowledge_graph(text):
    doc = nlp(text)
    edges = []
    for sent in doc.sents:
        for token in sent:
            if token.dep_ in ("nsubj", "dobj") and token.head.pos_ == "VERB":
                edges.append((token.head.lemma_, token.lemma_))
    graph = nx.DiGraph()
    graph.add_edges_from(edges)
    return graph

# Function to display graph using pyvis
def display_graph(graph):
    net = Network(height="600px", width="100%", directed=True)
    for node in graph.nodes:
        net.add_node(node, label=node)
    for source, target in graph.edges:
        net.add_edge(source, target)

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        path = tmp_file.name
        net.show(path)

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
        components.html(html, height=600, scrolling=True)

    os.remove(path)

# Input options
option = st.radio("Select Input Type", ["PDF", "URL", "Text"])

text = ""
if option == "PDF":
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)

elif option == "URL":
    url = st.text_input("Enter URL")
    if url:
        text = extract_text_from_url(url)

elif option == "Text":
    text = st.text_area("Enter Text")

# Generate graph
if st.button("Generate Knowledge Graph") and text:
    graph = generate_knowledge_graph(text)
    display_graph(graph)
elif st.button("Generate Knowledge Graph"):
    st.warning("Please provide some content first.")
