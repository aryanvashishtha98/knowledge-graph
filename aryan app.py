import streamlit as st
import spacy
import subprocess
import sys
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import re

# Download spaCy model if not available
try:
    nlp = spacy.load("en_core_web_sm")
except:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

st.set_page_config(page_title="Knowledge Graph Generator", layout="wide")
st.title("Knowledge Graph Generator from PDF")

st.markdown("### Upload a PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    # Extract text from PDF
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    st.markdown("### Extracted Text")
    st.write(text[:1000])  # Limit preview to first 1000 chars

    # Run spaCy for entity recognition
    st.markdown("### Named Entities")
    doc = nlp(text)
    ents = [(ent.text, ent.label_) for ent in doc.ents]
    if ents:
        for ent, label in ents:
            st.write(f"**{label}** → {ent}")
    else:
        st.write("No entities found.")

    # Optional: Display a knowledge graph structure (basic)
    st.markdown("### Entity Pairs (Mock Graph)")
    for i in range(len(ents)-1):
        st.write(f"{ents[i][0]} → {ents[i+1][0]}")

