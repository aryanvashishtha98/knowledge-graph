@echo off
cd /d C:\Users\Asus\Desktop\KnowledgeGraph

REM Create virtual environment if not exists
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install project dependencies
pip install streamlit pyvis PyPDF2 beautifulsoup4 spacy networkx

REM Download spaCy language model
python -m spacy download en_core_web_sm

echo Installation complete. You can now run the app using run_knowledgegraph.bat
pause
