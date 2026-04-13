# Command line: streamlit run app.py
# python -m streamlit run src/app.py
from utils import st
from config import available_img_models, available_llm_models  # Import model options
# Question: What tasks need to be done after backing up PROD to CLONE5?

st.set_page_config(
    page_title="RAG Q&A System",
    page_icon="🤖",
    layout="wide"
)

st.title("RAG Q&A System 🎯")
st.markdown("""
### Welcome to the system. Please select a function from the left menu:

- 📂 **Knowledge_Interface**: Upload files and create a vector database  
- 💬 **Answering_Interface**: Enter questions and get LLM answers
""")

# Initialize model setting parameters (only on first execution)
if "model_settings" not in st.session_state:
    st.session_state.model_settings = {
        "img_model": available_img_models[0],
        "llm_model": available_llm_models[0],
        "temperature": 0.0,
        "top_p": 0.95,
        "top_n": 10,
        "top_k": 5,
        "search_method": "Basic",
        "chunk_size": 200,
        "chunk_overlap": 50
    }