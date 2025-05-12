import streamlit as st
import PyPDF2
import requests
from bs4 import BeautifulSoup
import spacy
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text()
    except Exception as e:
        return f"Error fetching URL: {e}"

def create_knowledge_graph(text):
    doc = nlp(text)
    G = nx.Graph()
    for sent in doc.sents:
        for token in sent:
            if token.dep_ in ("nsubj", "dobj"):
                source = token.head.text
                target = token.text
                G.add_edge(source, target)
    return G

def display_graph(graph):
    net = Network(notebook=False)
    for node in graph.nodes:
        net.add_node(node, label=node)
    for edge in graph.edges:
        net.add_edge(edge[0], edge[1])
    tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, "graph.html")
    net.show(path)
    with open(path, "r", encoding="utf-8") as file:
        html = file.read()
    return html

# Streamlit UI
st.title("Knowledge Graph Generator")
st.markdown("Upload a PDF, enter a URL, or type text to generate a knowledge graph.")

option = st.radio("Choose input type:", ["PDF", "URL", "Text"])

text_data = ""

if option == "PDF":
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    if uploaded_file:
        text_data = extract_text_from_pdf(uploaded_file)

elif option == "URL":
    url = st.text_input("Enter URL")
    if st.button("Fetch URL Content"):
        if url:
            text_data = extract_text_from_url(url)

elif option == "Text":
    text_data = st.text_area("Enter text")

if text_data:
    st.success("Text extracted successfully.")
    graph = create_knowledge_graph(text_data)
    st.subheader("Knowledge Graph")
    html = display_graph(graph)
    st.components.v1.html(html, height=600, scrolling=True)
