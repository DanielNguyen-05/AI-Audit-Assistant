import os
import streamlit as st
from src.vlm_processor import process_pdf_to_json
from src.rag_engine import create_vector_store
from src.agent import create_audit_agent

# --- Cấu hình giao diện ---
st.set_page_config(page_title="AI Audit Assistant", page_icon="📊", layout="wide")
st.title("📊 Trợ lý Kiểm toán Đa phương thức (Agentic RAG)")
st.markdown("Hỗ trợ tự động đọc chứng từ scan và đối chiếu chuẩn mực (VAS/IFRS).")

# --- Tạo thư mục tạm nếu chưa có ---
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/vector_store", exist_ok=True)

# --- Sidebar: Xử lý file Upload ---
with st.sidebar:
    st.header("1. Tải lên Chứng từ")
    uploaded_file = st.file_uploader("Upload file PDF (Hợp đồng, BCTC scan...)", type=["pdf"])
    
    if uploaded_file is not None:
        file_path = os.path.join("data/raw", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        if st.button("🚀 Xử lý Dữ liệu (VLM + RAG)"):
            with st.status("Đang phân tích tài liệu...", expanded=True) as status:
                try:
                    st.write("1. Đang dùng AI Vision đọc ảnh PDF...")
                    json_path = process_pdf_to_json(file_path, "data/processed")
                    
                    st.write("2. Đang băm nhỏ và lưu vào Vector Database...")
                    faiss_path = create_vector_store(json_path)
                    
                    # Lưu đường dẫn FAISS vào session để dùng cho chat
                    st.session_state["faiss_path"] = faiss_path
                    st.session_state["agent"] = create_audit_agent(faiss_path)
                    
                    status.update(label="Xử lý thành công!", state="complete", expanded=False)
                    st.success("Tài liệu đã sẵn sàng để tra cứu!")
                except Exception as e:
                    status.update(label="Có lỗi xảy ra", state="error")
                    st.error(f"Lỗi: {e}")

# --- Màn hình chính: Giao diện Chat ---
st.header("2. Không gian Truy vấn AI")

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Tôi là Trợ lý Kiểm toán AI. Hãy hỏi tôi về các điều khoản ghi nhận doanh thu hoặc các bút toán trong tài liệu bạn vừa tải lên."}
    ]

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Khung nhập câu hỏi
if prompt := st.chat_input("VD: Theo hợp đồng vừa upload, doanh thu được ghi nhận khi nào?"):
    if "agent" not in st.session_state:
        st.warning("Vui lòng upload và xử lý tài liệu ở cột bên trái trước khi hỏi!")
    else:
        # Hiển thị câu hỏi của user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI suy luận và trả lời
        with st.chat_message("assistant"):
            with st.spinner("Đang suy luận và tra cứu chứng từ..."):
                agent = st.session_state["agent"]
                response = agent.invoke({"messages": [("user", prompt)]})
                answer = response["messages"][-1].content
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})