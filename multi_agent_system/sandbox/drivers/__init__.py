"""
multi_agent_system.sandbox.drivers
==================================
Factory cung cấp Driver tương ứng cho từng ngôn ngữ: Python, Java, C.
"""

from .base import BaseMultiFileDriver
from .python_driver import PythonMultiFileDriver
from .java_driver import JavaMultiFileDriver
from .c_driver import CMultiFileDriver

class MultiFileDriverFactory:
    _drivers = {
        "python": PythonMultiFileDriver(),
        "java": JavaMultiFileDriver(),
        "c": CMultiFileDriver()
    }

    @classmethod
    def get_driver(cls, language: str) -> BaseMultiFileDriver:
        lang_key = language.lower().strip()
        if lang_key in ["c", "cpp", "c++"]:
            lang_key = "c"
        driver = cls._drivers.get(lang_key)
        if not driver:
            raise ValueError(f"Ngôn ngữ '{language}' chưa được hỗ trợ Driver Sandbox.")
        return driver
