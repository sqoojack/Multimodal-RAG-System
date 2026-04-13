# Answering_Interface.py
from utils import os, json, st 
from langchain_core.documents import Document 
from UI_model_select import render_model_settings_ui  
from RAG_Embedding import load_vectorstore
from RAG_LLM_Generator import llm_generator, extract_answer_and_thought 
from RAG_Evaluation import evaluate_rag_result
from reranking import search_top_k, rerank_chunks_top_k  
from full_file import generate_full_files_answer  # Custom RAG logic
from config import default_model_settings, ollama_url, VECTOR_DB_DIR, reranking_url, reranking_api, cert_datapath  

# Set Streamlit page info
st.set_page_config(page_title="Q&A Interface", page_icon="💬")
st.title("💬 Q&A Interface")

# Initialize model_settings (from Session State or apply defaults)
if "model_settings" not in st.session_state:
    st.session_state.model_settings = default_model_settings.copy()

# Initialize vector database and document list
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "docs" not in st.session_state:
    st.session_state.docs = []
if "qa_result" not in st.session_state:
    st.session_state.qa_result = None

# Search local directory for all vector databases (folder name = DB name)
vector_db_names = [f for f in os.listdir(VECTOR_DB_DIR) if os.path.isdir(os.path.join(VECTOR_DB_DIR, f))]

# Use selectbox to let user choose a database
selected_db = st.selectbox("📂 **Select an existing vector database**", options=vector_db_names)

# Attempt to load vector data and raw documents if user selected a database
if selected_db:
    try:
        db_path = os.path.join(VECTOR_DB_DIR, selected_db)

        # Load vector database (via Ollama's Embedding Model)
        vectorstore = load_vectorstore(
            db_path,
            embedding_model=st.session_state.model_settings.get("embedding_model", "bge-m3"),
        )
        st.session_state.vectorstore = vectorstore

        # Read raw text content (e.g., page content and source info) into docs
        metadata_path = os.path.join(db_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata_list = json.load(f)

            docs_list = []
            if isinstance(metadata_list, list):
                # metadata.json is in List format
                for meta in metadata_list:
                    page_content = meta.get("page_content", "")
                    meta_data = meta.get("metadata", {})
                    docs_list.append(Document(page_content=page_content, metadata=meta_data))
            elif isinstance(metadata_list, dict):
                # metadata.json is in a single Document format
                page_content = metadata_list.get("page_content", "")
                meta_data = metadata_list.get("metadata", {})
                docs_list.append(Document(page_content=page_content, metadata=meta_data))
            st.session_state.docs = docs_list
        else:
            st.session_state.docs = []

    except Exception as e:
        st.error(f"❌ Failed to load vector database: {e}")
        st.stop()
else:
    st.warning("⚠️ No vector database created yet. Please go to the 'Create Knowledge Base' page to upload files.")
    st.stop()

# Display LLM model and parameter settings menu (top_p, temperature, etc.)
render_model_settings_ui()

# User inputs question
query = st.text_area("**Please enter your question**", value="What are the regulations regarding notice periods and severance pay calculations?")

# Start Q&A process
if st.button("Get Answer"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Retrieving..."):
                # Choose search method based on settings: Basic / Reranking / MMR / Custom RAG
                search_method = st.session_state.model_settings.get("search_method", "Basic")
                vectorstore = st.session_state.vectorstore

                if search_method == "MMR":
                    # Use Maximal Marginal Relevance retrieval
                    retriever = vectorstore.as_retriever(
                        search_type="mmr",
                        search_kwargs={"k": st.session_state.model_settings.get("top_k", 5), "fetch_k": st.session_state.model_settings.get("top_n", 10), "lambda_mult": 0.5}
                    )
                    mmr_docs = retriever.invoke(query)
                    top_chunks = [(doc, 1.0) for doc in mmr_docs]
                    st.success("✅ MMR retrieval complete.")

                elif search_method in ["Reranking", "Custom RAG"]:
                    # Use vector search to obtain top_k candidate chunks initially
                    candidates = search_top_k(query, vectorstore, top_k=st.session_state.model_settings.get("top_n", 10))
                    # Further refine top_k chunks using Reranker
                    top_chunks = rerank_chunks_top_k(
                        query,
                        candidates,
                        top_k=st.session_state.model_settings.get("top_k", 5),
                        reranking_url=reranking_url,
                        reranking_api=reranking_api,
                        cert_datapath=cert_datapath
                    )
                    st.success("✅ Reranking complete.")

                else:
                    # Use basic vector Top-K search
                    top_chunks = search_top_k(
                        query,
                        vectorstore,
                        top_k=st.session_state.model_settings.get("top_k", 5)
                    )
                    st.success("✅ Basic retrieval complete.")

            with st.spinner("Generating answer..."):
                if search_method == "Custom RAG":
                    # Use full file info combined with chunks for answer (suitable for long docs)
                    file_chunks, answer = generate_full_files_answer(
                        top_chunks,
                        st.session_state.docs,
                        query,
                        ollama_url,
                        st.session_state.model_settings
                    )
                else:
                    # Send query + top_chunks to LLM model to generate answer
                    answer = llm_generator(
                        query,
                        top_chunks,
                        ollama_url,
                        llm_model=st.session_state.model_settings.get("llm_model"),
                        temperature=st.session_state.model_settings.get("temperature", 0.0),
                        top_p=st.session_state.model_settings.get("top_p", 1.0),
                    )

                # Separate LLM output: final answer vs thought process
                ans, thought = extract_answer_and_thought(answer)
                eval_chunks = file_chunks if search_method == "Custom RAG" else top_chunks
                
                st.session_state.qa_result = {
                    "query": query,
                    "ans": ans,
                    "thought": thought,
                    "eval_chunks": eval_chunks,
                    "search_method": search_method
                }

                
        except Exception as e:
            st.error(f"❌ Error occurred: {e}")
            
if st.session_state.qa_result is not None:
    res = st.session_state.qa_result
    
    # Split into left/right blocks to show answer and source chunks
    left, right = st.columns([2, 1])
    with left:
        st.markdown("### 📘 Answer:")
        st.markdown(res["ans"])  # Retrieve ans from res
        if res["thought"]:       # Retrieve thought from res
            with st.expander("💭 Thought Process"):
                st.markdown(res["thought"])
                
    with right:
        st.markdown("### 🔍 Matched Paragraphs:")
        # Retrieve search_method and eval_chunks from res
        if res["search_method"] == "Custom RAG":
            for i, doc in enumerate(res["eval_chunks"]):
                with st.expander(f"Paragraph {i+1} | Source: {doc.metadata.get('source')}"):
                    st.write(doc.page_content)
        else:
            for i, item in enumerate(res["eval_chunks"]):
                # Format for general retrieval is tuple: (doc, score)
                doc, score = item
                with st.expander(f"Rank {i+1} | Source: {doc.metadata.get('source')} | Score: {score:.2f}"):
                    st.write(doc.page_content)

    # Add RAG system evaluation block (now placed outside)
    st.divider()
    st.markdown("### 📊 RAG System Performance Evaluation")
    
    if st.button("Run Ragas Metric Evaluation (Consumes compute resources)"):
        with st.spinner("LLM is performing cross-validation (Faithfulness, Answer Relevance)..."):
            try:
                eval_df = evaluate_rag_result(
                    query=res["query"],
                    answer=res["ans"],
                    top_chunks=res["eval_chunks"],
                    ollama_url=ollama_url,
                    # llm_model=st.session_state.model_settings.get("llm_model"),
                    llm_model="deepseek-r1:8b",
                    embeddings=st.session_state.vectorstore.embeddings 
                )
                st.success("Evaluation complete.")
                st.dataframe(eval_df[["faithfulness", "answer_relevancy"]], use_container_width=True)
            except Exception as eval_e:
                st.error(f"Error occurred during evaluation: {eval_e}")