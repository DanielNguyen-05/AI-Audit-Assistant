import os
import json
import base64
import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configs.system_prompts import VLM_EXTRACTION_PROMPT
from src.utils import mask_sensitive_data

load_dotenv()

def get_base64_image(page, zoom=2.0):
    """Chuyển đổi 1 trang PDF thành chuỗi Base64 Image để gửi cho VLM"""
    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix, alpha=False)
    return base64.b64encode(pixmap.tobytes("png")).decode("utf-8")

def extract_text_from_image(image_b64: str, page_num: int) -> str:
    """Gọi API FPT Qwen2.5-VL để đọc chữ từ ảnh"""
    api_key = os.getenv("FPT_AI_KIE_KEY")
    endpoint = os.getenv("FPT_AI_KIE_ENDPOINT")
    model = os.getenv("FPT_AI_KIE_MODEL")

    if not api_key:
        raise ValueError("Chưa cấu hình FPT_AI_KIE_KEY trong file .env")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "api-key": api_key
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": VLM_EXTRACTION_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    },
                    {
                        "type": "text",
                        "text": f"Hãy đọc nội dung trang số {page_num}."
                    }
                ]
            }
        ],
        "temperature": 0.0 # Giữ temperature = 0 để AI không tự bịa :))
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Lỗi khi gọi API VLM ở trang {page_num}: {e}")
        return ""

def process_pdf_to_json(pdf_path: str, output_dir: str):
    """Xử lý toàn bộ file PDF và lưu kết quả ra file JSON"""
    print(f"Đang xử lý file: {pdf_path}...")
    doc = fitz.open(pdf_path)
    extracted_data = []

    for i in range(len(doc)):
        print(f"  - Đang đọc trang {i+1}/{len(doc)}")
        img_b64 = get_base64_image(doc[i])
        raw_text = extract_text_from_image(img_b64, i+1)
                
        # Gọi hàm che dữ liệu nhạy cảm trước khi lưu
        safe_text = mask_sensitive_data(raw_text)
        
        extracted_data.append({
            "page": i + 1,
            "content": safe_text
        })

    # Lưu file JSON
    filename = os.path.basename(pdf_path).replace(".pdf", "_data.json")
    output_path = os.path.join(output_dir, filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"document": filename, "pages": extracted_data}, f, ensure_ascii=False, indent=4)
    
    print(f"Đã lưu kết quả tại: {output_path}")
    return output_path