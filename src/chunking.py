# src/chunking.py
import os
import json
import webvtt

def process_vtt_to_chunks(raw_dir="data/raw", output_file="data/processed/chunks_metadata.json", window_size=10, overlap=5):
    all_metadata = []
    
    # Quét tất cả file VTT trong thư mục raw
    for filename in os.listdir(raw_dir):
        if not filename.endswith('.vtt'): continue
            
        video_id = filename.split('.')[0]
        filepath = os.path.join(raw_dir, filename)
        
        # Đọc VTT
        vtt = webvtt.read(filepath)
        captions = []
        for caption in vtt:
            h, m, s = caption.start.split(':')
            seconds = int(h) * 3600 + int(m) * 60 + float(s)
            captions.append({
                'text': caption.text.replace('\n', ' ').strip(),
                'start': int(seconds)
            })
            
        # Sliding Window Chunking
        step = window_size - overlap
        for i in range(0, len(captions), step):
            segment = captions[i:i+window_size]
            if not segment: break
                
            text_chunk = " ".join([item['text'] for item in segment])
            start_time = segment[0]['start']
            
            all_metadata.append({
                "video_id": video_id,
                "start_time": start_time,
                "text": text_chunk
            })
            
    # Lưu toàn bộ ra file JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, ensure_ascii=False, indent=4)
        
    print(f"Đã tạo xong {len(all_metadata)} chunks và lưu vào {output_file}")