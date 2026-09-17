"""
multi_agent_system.sandbox.drivers.base
======================================
Lớp cơ sở trừu tượng cho các Driver thực thi đa tệp (Multi-file Drivers).
"""

import os
from abc import ABC, abstractmethod
from typing import Dict

class BaseMultiFileDriver(ABC):
    """
    Interface Driver hỗ trợ chuẩn bị Workspace đa tệp và tạo kịch bản thực thi.
    """
    @abstractmethod
    def prepare_workspace(
        self, 
        files: Dict[str, str], 
        test_cases: str, 
        host_dir: str, 
        use_docker: bool = False
    ) -> str:
        """
        Ghi toàn bộ các tệp mã nguồn theo đúng cấu trúc cây thư mục,
        tạo mã kiểm thử (Test Harness), và trả về chuỗi lệnh CLI để khởi chạy.
        """
        pass

    @staticmethod
    def write_files(files: Dict[str, str], host_dir: str):
        """Hàm tiện ích ghi danh sách file {relative_path: content} vào host_dir."""
        for rel_path, content in files.items():
            clean_rel = rel_path.lstrip("/\\")
            target_path = os.path.join(host_dir, clean_rel)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
