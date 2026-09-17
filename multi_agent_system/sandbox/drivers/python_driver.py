"""
multi_agent_system.sandbox.drivers.python_driver
===============================================
Driver thực thi đa tệp dành cho ngôn ngữ Python.
"""

import os
from typing import Dict
from .base import BaseMultiFileDriver

class PythonMultiFileDriver(BaseMultiFileDriver):
    def prepare_workspace(
        self, 
        files: Dict[str, str], 
        test_cases: str, 
        host_dir: str, 
        use_docker: bool = False
    ) -> str:
        # 1. Ghi toàn bộ các tệp mã nguồn
        self.write_files(files, host_dir)

        # 2. Đảm bảo các thư mục con có file __init__.py để hỗ trợ package import
        for root, dirs, _ in os.walk(host_dir):
            if root != host_dir:
                init_file = os.path.join(root, "__init__.py")
                if not os.path.exists(init_file):
                    with open(init_file, "w", encoding="utf-8") as f:
                        f.write("# Package init\n")

        # 3. Tạo test_harness.py
        harness_code = f"""import sys
import os
import unittest

# Đảm bảo đường dẫn workspace nằm đầu PYTHONPATH
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

{test_cases}

if __name__ == "__main__":
    unittest.main()
"""
        harness_path = os.path.join(host_dir, "test_harness.py")
        with open(harness_path, "w", encoding="utf-8") as f:
            f.write(harness_code)

        # 4. Phân tách danh sách file mã nguồn dự án (Coder) và file test_harness.py (Tester)
        # Thực hiện cơ chế kiểm thử 2 giai đoạn (2-Phase Verification):
        # Giai đoạn 1: Dùng `py_compile` kiểm tra toàn bộ cú pháp (Syntax/Indent) các file .py dự án.
        # Giai đoạn 2: Chỉ khi cú pháp mã nguồn hợp lệ mới thực thi kịch bản kiểm thử `test_harness.py`.
        import glob
        py_files = glob.glob(os.path.join(host_dir, "**", "*.py"), recursive=True)
        harness_abs = os.path.abspath(harness_path)
        project_py_files = [pf for pf in py_files if os.path.abspath(pf) != harness_abs]

        if project_py_files:
            py_sources_str = " ".join([f'"{os.path.relpath(pf, host_dir).replace(chr(92), "/")}"' for pf in project_py_files])
            if use_docker:
                return (
                    "sh -c 'python3 -m py_compile $(find /workspace -name \"*.py\" ! -name \"test_harness.py\") && "
                    "python3 /workspace/test_harness.py'"
                )
            # Local execution
            return f"python -m py_compile {py_sources_str} && python test_harness.py"
        else:
            if use_docker:
                return "python3 /workspace/test_harness.py"
            return "python test_harness.py"
