# src/embedding.py
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def build_faiss_index(metadata_file="data/processed/chunks_metadata.json", index_file="data/vector_db/course_index.index"):
    print("Đang tải mô hình Embedding...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    if not metadata:
        print("Không có dữ liệu để nhúng!")
        return
        
    chunks = [item["text"] for item in metadata]
    
    print(f"Bắt đầu nhúng {len(chunks)} đoạn văn bản (Quá trình này có thể mất vài phút trên CPU)...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    faiss.write_index(index, index_file)
    print(f"Đã lưu FAISS index thành công tại: {index_file}")