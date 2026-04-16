import os
import json
import yaml
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Đọc file cấu hình yaml
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

def create_vector_store(json_path: str):
    """Đọc file JSON, chia nhỏ văn bản và tạo Vector DB (FAISS)"""
    print(f"Đang tạo Vector Store cho: {json_path}")
    
    # 1. Load data
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    documents = []
    doc_name = data.get("document", "Unknown")
    
    for page in data.get("pages", []):
        # Gắn metadata để lúc Agent trả lời biết được đoạn text nằm ở trang nào
        meta = {"source": doc_name, "page": page["page"]}
        documents.append(Document(page_content=page["content"], metadata=meta))

    # 2. Split text (Băm nhỏ văn bản)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["rag"]["chunk_size"],
        chunk_overlap=config["rag"]["chunk_overlap"]
    )
    chunks = splitter.split_documents(documents)
    print(f"  - Đã chia thành {len(chunks)} đoạn nhỏ.")

    # 3. Create Embeddings (Dùng model chạy local cho nhẹ và miễn phí)
    embeddings = HuggingFaceEmbeddings(model_name=config["rag"]["embedding_model"])
    
    # 4. Build FAISS
    vector_db = FAISS.from_documents(chunks, embeddings)
    
    # 5. Lưu xuống ổ cứng
    db_name = os.path.basename(json_path).replace("_data.json", "_faiss")
    save_path = os.path.join(config["system"]["vector_store_dir"], db_name)
    vector_db.save_local(save_path)
    
    print(f"  - Đã lưu Vector Store tại: {save_path}")
    return save_path

def get_retriever(faiss_path: str):
    """Load Vector DB từ ổ cứng và tạo công cụ tìm kiếm cho Agent"""
    embeddings = HuggingFaceEmbeddings(model_name=config["rag"]["embedding_model"])
    
    # Bật allow_dangerous_deserialization vì dữ liệu do chính chúng ta tạo ra (FAISS yêu cầu)
    vector_db = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
    
    # Trả về retriever để Agent dùng
    return vector_db.as_retriever(search_kwargs={"k": config["rag"]["top_k"]})