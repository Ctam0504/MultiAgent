"""
File khởi chạy nhanh Hệ thống Multi-Agent Code Generation Đa Tệp
=============================================================
Lưu ý:
  - Mọi tham số hệ thống (bật/tắt share memory, số vòng lặp cycles, sandbox, model...) 
    đều được chỉnh sửa trực tiếp trong file: multi_agent_system/config.py
  - Khi chạy chỉ cần nhập task:
      python run_mas.py --task "Hoàn thiện project dang dở"
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from multi_agent_system.main import main

if __name__ == "__main__":
    main()
