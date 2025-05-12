import streamlit as st
import PyPDF2
import requests
from bs4 import BeautifulSoup
import spacy
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# PDF text extraction
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# Webpage text extraction
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

# Knowledge graph creation
def generate_knowledge_graph(text):
    doc = nlp(text)
    G = nx.Graph()
    for sent in doc.sents:
        entities = [ent.text.strip() for ent in sent.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'NORP', 'EVENT']]
        for i in range(len(entities) - 1):
            G.add_edge(entities[i], entities[i + 1])
    return G

# Display the graph in a temp file
def display_graph(G):
    if len(G.nodes) == 0:
        return None

    net = Network(height="500px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)

    temp_dir = tempfile.gettempdir()  # ✅ Safe temp directory
    file_name = "graph.html"          # ✅ Simple file name
    abs_path = os.path.join(temp_dir, file_name)  # ✅ Safe path

    net.write_html(abs_path)          # ✅ Write the HTML safely
    return abs_path

# ---------- Streamlit Interface ----------

st.set_page_config(page_title="Knowledge Graph Generator", layout="centered")
st.title("🧠 Knowledge Graph Generator")

input_type = st.radio("Select input type:", ["Text", "PDF", "URL"])

if input_type == "Text":
    user_text = st.text_area("Enter your content here:")
    if st.button("Generate Graph") and user_text.strip():
        G = generate_knowledge_graph(user_text)
        path = display_graph(G)
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=550)
        else:
            st.warning("No entities found. Try with more detailed text.")

elif input_type == "PDF":
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file and st.button("Generate Graph"):
        text = extract_text_from_pdf(uploaded_file)
        G = generate_knowledge_graph(text)
        path = display_graph(G)
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=550)
        else:
            st.warning("No entities found in the PDF.")

elif input_type == "URL":
    url = st.text_input("Enter the URL of a webpage:")
    if url and st.button("Generate Graph"):
        try:
            text = extract_text_from_url(url)
            G = generate_knowledge_graph(text)
            path = display_graph(G)
            if path and os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    st.components.v1.html(f.read(), height=550)
            else:
                st.warning("No entities found from the URL.")
        except Exception as e:
            st.error(f"Failed to fetch content: {e}")
