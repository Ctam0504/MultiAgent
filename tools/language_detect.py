from pathlib import Path
from magika import Magika

def check_my_files(file_paths: list):
    m = Magika()
    mapping = {'python': 'Python', 'java': 'Java', 'c': 'C'}
    
    for path_str in file_paths:
        path = Path(path_str)
        try:
            result = m.identify_path(path)
            # Dùng .label thay cho .ct_label để hết Warning
            detected = result.output.label.lower()
            
            lang_name = mapping.get(detected, f"Khác ({result.output.label})")
            print(f"File [{path.name}] -> Ngôn ngữ: {lang_name}")
            
        except Exception as e:
            print(f"Lỗi khi đọc file [{path_str}]: {e}")

# Dùng r"..." (Raw String) để tránh lỗi SyntaxWarning do dấu '\' trên Windows
my_3_files = [
    r"D:\Thesis\GraphRAG\c\calculator.h",
    r"D:\Thesis\GraphRAG\python\database.py",
    r"D:\Thesis\GraphRAG\java\TicketBookingService.java"
]

check_my_files(my_3_files)