from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
 
def get_rag_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = FAISS.load_local("rag/vectorstore", embeddings, allow_dangerous_deserialization=True)
    llm = HuggingFacePipeline.from_model_id(
        model_id="gpt2",
        task="text-generation",
        pipeline_kwargs={"max_new_tokens": 50}
    )
    
    retriever = db.as_retriever()
    
    def invoke(query_dict):
        query = query_dict.get("input", "")
        docs = retriever.invoke(query)
        context = "\n".join([doc.page_content for doc in docs])
        prompt = f"{context}\n\nQuestion: {query}\nAnswer:"
        answer = llm.invoke(prompt)
        return {"answer": answer}
    
    class SimpleChain:
        def invoke(self, query_dict):
            return invoke(query_dict)
    
    return SimpleChain()
