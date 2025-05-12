import streamlit as st
import PyPDF2
from bs4 import BeautifulSoup
from pyvis.network import Network
import networkx as nx
import os
import tempfile
import spacy
import subprocess
import importlib.util

# --- Ensure the spaCy model is available ---
model_name = "en_core_web_sm"
if importlib.util.find_spec(model_name) is None:
    subprocess.run(["python", "-m", "spacy", "download", model_name])

nlp = spacy.load(model_name)

# --- Function to extract text from PDF ---
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# --- Function to create knowledge graph ---
def create_knowledge_graph(text):
    doc = nlp(text)
    G = nx.Graph()
    for ent in doc.ents:
        G.add_node(ent.text, label=ent.label_)
    for i in range(len(doc.ents) - 1):
        G.add_edge(doc.ents[i].text, doc.ents[i + 1].text)
    return G

# --- Function to display knowledge graph in Streamlit ---
def display_graph(G):
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    for node, attr in G.nodes(data=True):
        net.add_node(node, label=node, title=attr["label"])
    for source, target in G.edges():
        net.add_edge(source, target)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.show(tmp_file.name)
    return tmp_file.name

# --- Streamlit App UI ---
st.title("Knowledge Graph Generator from PDF")

pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])

if pdf_file is not None:
    text = extract_text_from_pdf(pdf_file)
    st.subheader("Extracted Text")
    st.write(text)

    if st.button("Generate Knowledge Graph"):
        G = create_knowledge_graph(text)
        html_path = display_graph(G)
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=600, scrolling=True)
