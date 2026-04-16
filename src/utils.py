import re

def mask_sensitive_data(text: str) -> str:
    """
    Hàm ẩn danh dữ liệu cá nhân (PII) và thông tin nhạy cảm.
    Giúp hệ thống đáp ứng tiêu chuẩn đạo đức và bảo mật dữ liệu.
    """
    if not text:
        return text
        
    # 1. Ẩn Số điện thoại Việt Nam (Bắt đầu bằng 0 hoặc 84, theo sau là 8-9 số)
    phone_pattern = r'\b(0|84)(3|5|7|8|9)[0-9]{8}\b'
    text = re.sub(phone_pattern, '[SĐT_ĐÃ_ẨN]', text)
    
    # 2. Ẩn Email
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    text = re.sub(email_pattern, '[EMAIL_ĐÃ_ẨN]', text)
    
    # 3. Ẩn Mã số thuế (10-13 số) hoặc CCCD (12 số)
    # Tìm các chuỗi chỉ chứa toàn số dài từ 10 đến 13 ký tự
    id_pattern = r'\b\d{10,13}\b'
    text = re.sub(id_pattern, '[MÃ_SỐ_ĐÃ_ẨN]', text)
    
    # Có thể mở rộng thêm logic để ẩn tên công ty cụ thể nếu cần nha mấy fen
    # company_pattern = r'(Công ty|CTY|TNHH|CP) [A-ZÀ-Ỹa-zà-ỹ\s]+'
    # text = re.sub(company_pattern, '[TÊN_DOANH_NGHIỆP]', text)
    
    return text