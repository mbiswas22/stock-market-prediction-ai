from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
 
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
 
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=db.as_retriever()
    )