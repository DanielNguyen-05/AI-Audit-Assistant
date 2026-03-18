# app.py
import os
from dotenv import load_dotenv
from src.youtube_scraper import extract_playlist_id, get_playlist_videos, download_subtitles
from src.chunking import process_vtt_to_chunks
from src.embedding import build_faiss_index
from src.llm_agent import CourseAssistant

load_dotenv()
YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def ingest_pipeline():
    print("\n--- BƯỚC 1: XÂY DỰNG KNOWLEDGE BASE ---")
    url = input("Nhập URL của Playlist YouTube: ")
    playlist_id = extract_playlist_id(url)
    
    if not playlist_id:
        print("Lỗi: URL không hợp lệ.")
        return
        
    print("1. Đang cào dữ liệu Playlist...")
    videos = get_playlist_videos(playlist_id, YOUTUBE_KEY)
    
    print(f"2. Bắt đầu tải phụ đề cho {len(videos)} video...")
    for vid in videos:
        download_subtitles(vid['video_id'])
        
    print("3. Làm sạch và Chunking dữ liệu (Sliding Window)...")
    process_vtt_to_chunks()
    
    print("4. Nhúng Vector và tạo FAISS Index...")
    build_faiss_index()
    print("ĐÃ HOÀN TẤT XÂY DỰNG DỮ LIỆU!\n")

def chat_pipeline():
    print("\n--- BƯỚC 2: RAG CHATBOT ---")
    if not os.path.exists("data/vector_db/course_index.index"):
        print("Chưa có cơ sở dữ liệu. Vui lòng chạy tính năng 1 trước!")
        return
        
    print("Đang khởi động Trợ lý AI...")
    assistant = CourseAssistant(GEMINI_KEY)
    
    while True:
        query = input("\nBạn muốn hỏi gì? (Gõ 'exit' để thoát): ")
        if query.lower() == 'exit': break
        
        print("\n⏳ Đang suy nghĩ...")
        answer, sources = assistant.ask(query)
        
        print("\n🤖 TRỢ LÝ AI TRẢ LỜI:")
        print("-" * 50)
        print(answer)
        print("-" * 50)
        print("📺 XEM CHI TIẾT TẠI VIDEO:")
        for i, url in enumerate(sources):
            print(f"[Nguồn {i+1}]: {url}")

if __name__ == "__main__":
    while True:
        print("\n" + "="*40)
        print("HỆ THỐNG RAG CHO KHÓA HỌC YOUTUBE")
        print("1. Tải Playlist & Xây dựng Knowledge Base")
        print("2. Chat với AI Trợ giảng")
        print("3. Thoát")
        
        choice = input("Chọn chức năng (1/2/3): ")
        if choice == '1':
            ingest_pipeline()
        elif choice == '2':
            chat_pipeline()
        elif choice == '3':
            break
        else:
            print("Lựa chọn không hợp lệ.")