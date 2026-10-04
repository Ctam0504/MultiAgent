import os

def generate_ascii_tree(dir_path: str, prefix: str = "") -> str:
    tree_str = ""
    ignore_dirs = {'.git', '__pycache__', 'node_modules', '.idea', 'target', 'bin', 'build', '.vscode'}
    
    if not os.path.exists(dir_path):
        return "(Thư mục không tồn tại / Dự án rỗng)\n"

    try:
        entries = sorted(os.listdir(dir_path))
        entries = [e for e in entries if e not in ignore_dirs]
        
        for i, entry in enumerate(entries):
            full_path = os.path.join(dir_path, entry)
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            
            tree_str += f"{prefix}{connector}{entry}\n"
            
            if os.path.isdir(full_path):
                new_prefix = prefix + ("    " if is_last else "│   ")
                tree_str += generate_ascii_tree(full_path, new_prefix)
    except Exception as e:
        return f"Lỗi quét thư mục: {str(e)}\n"
        
    return tree_str