"""
multi_agent_system.tools
========================
Module chứa các công cụ hỗ trợ hệ thống (nhận diện ngôn ngữ, phân tích tệp...)
"""

from .language_detector import detect_language_from_folder, detect_language_from_files

__all__ = ["detect_language_from_folder", "detect_language_from_files"]
