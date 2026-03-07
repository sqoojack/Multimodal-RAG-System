# RAG_Evaluation.py
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance
from langchain_ollama import ChatOllama

def evaluate_rag_result(query: str, answer: str, top_chunks: list, ollama_url: str, llm_model: str, embeddings) -> pd.DataFrame:
    """
    執行 RAG 自動化評估
    使用指標：
    - faithfulness: 評估生成的答案是否都來自檢索出的上下文 (防幻覺)。
    - answer_relevance: 評估生成的答案是否有效回答了使用者的問題。
    """
    # 提取檢索到的文本，若為 Custom RAG 則傳入對應的 file_chunks
    contexts = [doc.page_content for doc, _ in top_chunks] if isinstance(top_chunks[0], tuple) else [doc.page_content for doc in top_chunks]
    
    data = {
        "question": [query],
        "answer": [answer],
        "contexts": [contexts]
    }
    dataset = Dataset.from_dict(data)

    # Ragas 的 LLM 評審需要使用 Chat 模型介面，初始化本地 Ollama
    # 評審用的 LLM 溫度應設為 0 以確保評估結果一致性
    eval_llm = ChatOllama(model=llm_model, base_url=ollama_url, temperature=0.0)

    # 執行評估，覆寫 LLM 與 Embeddings
    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevance],
        llm=eval_llm,
        embeddings=embeddings,
        raise_exceptions=False
    )
    
    return result.to_pandas()