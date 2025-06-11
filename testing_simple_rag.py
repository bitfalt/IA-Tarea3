import os
import faiss
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Directory containing pdf and persistent storage
directory = os.path.dirname(os.path.abspath(__file__))
pdf_dir = os.path.join(directory, "Apuntadores")
persist_dir = os.path.join(directory, "vector_store")

if not os.path.exists(persist_dir):
    print("Chroma db not found, creating vector store...")

    # Load each PDF
    file_paths = [os.path.join(pdf_dir, fn) for fn in os.listdir(pdf_dir)]
    print(f"File paths: {file_paths}")
    loaders = [PyPDFLoader(fp) for fp in file_paths]
    documents = []
    for loader in loaders:
        documents.extend(loader.load())
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    index = faiss.IndexFlatL2(len(embeddings.embed_query("Hello world")))
    print(f"Page metadata: {documents[0].metadata}")
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )

    vector_store.add_documents(documents)
    vector_store.save_local(persist_dir)


