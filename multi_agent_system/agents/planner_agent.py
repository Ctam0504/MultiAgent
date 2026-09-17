"""
multi_agent_system.agents.planner_agent
======================================
Agent Planner: Tiếp nhận yêu cầu, phân tích cây thư mục bằng GraphRAG,
xác định ngôn ngữ qua công cụ, lập kế hoạch kiến trúc đa tệp và cập nhật plan
khi nhận phản hồi lỗi Global từ Reviewer.
"""

import os
from typing import Optional, Dict, Any
from .base_agent import BaseAgent
from ..schemas import MultiFilePlan, FileSpec, LanguageType
from ..tools.language_detector import detect_language_from_folder
from ..rag.ast_extractor import parse_codebase_to_graph_and_chunks
from ..rag.graph_store import GraphKnowledgeStore
from ..rag.rag_pipeline import GraphRAGRetriever
from .. import config

class PlannerAgent(BaseAgent):
    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        super().__init__(
            model_name=model_name or config.PLANNER_MODEL,
            base_url=base_url,
            temperature=0.1
        )

    def _get_language_guidelines(self, lang: str) -> str:
        lang_lower = lang.lower()
        if lang_lower == "java":
            return """
QUY TẮC BẮT BUỘC DÀNH CHO JAVA:
1. Mọi `filepath` phải có đuôi `.java` và tuân thủ chuẩn cấu trúc package (ví dụ: `models/User.java`, `services/UserService.java`).
2. Tên Class PHẢI TRÙNG KHỚP 100% với tên file `.java` (ví dụ: `public class User` trong `User.java`).
3. Khai báo `package` ở đầu mỗi file phù hợp với đường dẫn thư mục.
4. Đảm bảo import, dependancy đầy đủ giữa các package.
"""
        elif lang_lower in ["c", "cpp"]:
            return """
QUY TẮC BẮT BUỘC DÀNH CHO C:
1. Tạo đầy đủ các file Header (`.h`) cho interface/structs và file nguồn (`.c`) cho logic triển khai.
2. File Header PHẢI có Include Guards (`#ifndef ..._H`, `#define ..._H`, `#endif`).
3. Sử dụng `#include "relative_path/file.h"` để liên kết giữa các module.
4. Tách biệt rõ ràng giữa khai báo (Header) và triển khai (Source code).
"""
        else:  # python
            return """
QUY TẮC BẮT BUỘC DÀNH CHO PYTHON:
1. Tất cả `filepath` phải có đuôi `.py`.
2. Sử dụng import tương đối/tuyệt đối chuẩn xác dựa trên cấu trúc các tệp đã lên kế hoạch.
3. Đảm bảo cấu trúc module rõ ràng, phân chia tầng hợp lý.
"""

    async def plan_codebase(
        self, 
        task_prompt: str, 
        input_folder: Optional[str] = None, 
        target_language: Optional[str] = None,
        initial_files: Optional[Dict[str, str]] = None
    ) -> MultiFilePlan:
        """
        Khởi tạo kế hoạch đa tệp dựa trên yêu cầu bài toán và thư mục tiền sắp xếp.
        """
        # 1. Xác định ngôn ngữ lập trình
        resolved_lang: Optional[str] = target_language
        if not resolved_lang and input_folder and os.path.exists(input_folder):
            detected, _ = detect_language_from_folder(input_folder)
            if detected:
                resolved_lang = detected.value

        # Nếu không có thư mục sẵn, phân tích từ task_prompt
        if not resolved_lang and task_prompt:
            task_lower = task_prompt.lower()
            if any(k in task_lower for k in ["java", "spring", "springboot", "maven", "gradle"]):
                resolved_lang = "java"
            elif any(k in task_lower for k in ["c++", "cpp", "ngôn ngữ c", "lập trình c", " file .c", " file .h"]):
                resolved_lang = "c"
            elif any(k in task_lower for k in ["python", "django", "fastapi", "flask", "pytest"]):
                resolved_lang = "python"

        # Fallback theo cấu hình config.py (mặc định java hoặc giá trị người dùng cấu hình)
        if not resolved_lang:
            resolved_lang = getattr(config, "DEFAULT_TARGET_LANGUAGE", "java")

        # 2. Phân tích ngữ cảnh Codebase hiện hữu bằng GraphRAG nếu có
        graphrag_context = ""
        if input_folder and os.path.exists(input_folder):
            try:
                graph, chunks = parse_codebase_to_graph_and_chunks(input_folder)
                if graph.number_of_nodes() > 0:
                    store = GraphKnowledgeStore()
                    await store.build_from_chunks(graph, chunks)
                    retriever = GraphRAGRetriever(store)
                    graphrag_context = await retriever.retrieve_context(task_prompt, top_k=config.GRAPHRAG_TOP_K)
            except Exception as e:
                print(f"⚠️ [Planner] Bỏ qua trích xuất GraphRAG do lỗi: {e}")

        rag_section = f"\n### [NGỮ CẢNH CODEBASE TỪ ĐỒ THỊ GRAPHRAG]:\n{graphrag_context}\n" if graphrag_context else ""

        # 3. Tổng hợp danh sách tệp tiền sắp xếp của người dùng nếu có
        existing_files_section = ""
        if initial_files:
            file_summaries = []
            for fp, content in initial_files.items():
                first_lines = "\n".join([line for line in content.splitlines()[:20] if line.strip()])
                file_summaries.append(f"--- TỆP TIỀN SẮP XẾP: `{fp}` ---\n{first_lines}\n...")
            existing_files_section = f"""
### [CÁC TỆP TIỀN SẮP XẾP TRONG THƯ MỤC INPUT DO NGƯỜI DÙNG CUNG CẤP]:
{chr(10).join(file_summaries)}

QUY TẮC BẮT BUỘC ĐỐI VỚI THƯ MỤC TIỀN SẮP XẾP:
1. Bạn ĐANG LÀM VIỆC TRỰC TIẾP TRÊN THƯ MỤC ĐÃ ĐƯỢC NGƯỜI DÙNG SẮP XẾP TRƯỚC Ở TRÊN.
2. Hãy kế thừa, tái sử dụng các tệp, class, struct, hàm và package sẵn có trong thư mục này.
3. Trong danh sách `files`:
   - Nếu tệp đã có sẵn cần sửa đổi hoặc viết thêm logic: đặt `action: "MODIFY"`.
   - Nếu cần tạo thêm tệp mới: đặt `action: "CREATE"`.
   - Các tệp đã có sẵn nhưng KHÔNG cần sửa đổi gì thì vẫn liệt kê trong `files` với `action: "KEEP"` hoặc khai báo trong `dependencies` của các tệp khác.
"""

        # 4. Tạo Prompt lập kế hoạch kiến trúc
        guidelines = self._get_language_guidelines(resolved_lang)
        json_schema_desc = """
Trả về DUY NHẤT một JSON Object hợp lệ theo cấu trúc sau:
{
  "target_language": "%s",
  "architecture_pattern": "Mẫu kiến trúc sử dụng (vd: Clean Architecture, Modular)",
  "execution_order": ["filepath_leaf_1", "filepath_leaf_2", "filepath_root_main"],
  "files": [
    {
      "filepath": "đường dẫn tương đối của file kèm đuôi",
      "action": "CREATE hoặc MODIFY hoặc KEEP",
      "dependencies": ["các_file_mà_file_này_phụ_thuộc"],
      "purpose": "mục đích và trách nhiệm của tệp",
      "interface_summary": "chi tiết các Class, Function signatures, Structs hoặc Headers"
    }
  ],
  "rationale": "giải thích ngắn gọn lý do phân chia cấu trúc"
}
""" % resolved_lang

        prompt = f"""BẠN LÀ MỘT HỆ THỐNG SYSTEM ARCHITECT AGENT CHUYÊN NGHIỆP.
Nhiệm vụ: Phân tích yêu cầu bài toán và thiết kế cấu trúc ĐA TỆP (Multi-File) hoàn chỉnh cho ngôn ngữ: **{resolved_lang.upper()}**.

### [YÊU CẦU BÀI TOÁN]:
{task_prompt}
{existing_files_section}
{rag_section}
### [QUY TẮC THIẾT KẾ KIẾN TRÚC]:
1. Thiết kế module hóa sạch sẽ, tách biệt trách nhiệm (Single Responsibility).
2. Chuỗi trong mảng `execution_order` PHẢI KHỚP TỪNG KÝ TỰ với `filepath` trong danh sách `files`.
3. Sắp xếp `execution_order` theo thứ tự Topo: File độc lập (Data Models/Headers/Interfaces) đứng trước, file cài đặt đứng giữa, file tích hợp chính (Main/Service) đứng cuối cùng.
{guidelines}

### [ĐỊNH DẠNG ĐẦU RA YÊU CẦU]:
Chỉ trả về JSON object thuần túy, không chèn lời mở đầu hay kết luận ngoài JSON.
{json_schema_desc}
"""

        response_text = self.call_llm(prompt, format_json=True)
        json_obj = self.extract_json_object(response_text)

        if not json_obj or "files" not in json_obj:
            # Fallback tối thiểu nếu LLM không trả về JSON chuẩn
            default_file = f"solution.{'py' if resolved_lang == 'python' else ('java' if resolved_lang == 'java' else 'c')}"
            return MultiFilePlan(
                target_language=resolved_lang,
                architecture_pattern="Single Module Fallback",
                execution_order=[default_file],
                files=[
                    FileSpec(
                        filepath=default_file,
                        action="CREATE",
                        dependencies=[],
                        purpose="Triển khai toàn bộ giải pháp cho bài toán",
                        interface_summary="Tất cả các hàm và class cần thiết"
                    )
                ],
                rationale="Fallback do LLM trả về cấu trúc không chuẩn."
            )

        return MultiFilePlan.model_validate(json_obj)

    def refine_plan(
        self,
        current_plan: MultiFilePlan,
        reviewer_instructions: str,
        current_files: Dict[str, str],
        error_log: str
    ) -> MultiFilePlan:
        """
        Cập nhật lại kế hoạch và cây thư mục khi Reviewer xác định lỗi Global.
        """
        guidelines = self._get_language_guidelines(current_plan.target_language)
        files_overview = "\n".join([f"- {f.filepath}: {f.purpose}" for f in current_plan.files])

        prompt = f"""BẠN LÀ SYSTEM ARCHITECT AGENT.
Kế hoạch đa tệp hiện tại của bạn đã gặp **LỖI TOÀN CỤC (GLOBAL ARCHITECTURE ERROR)**: Mâu thuẫn interface, sai import, hoặc lệch tên hàm giữa các file.

### [KẾ HOẠCH HIỆN TẠI]:
Kiến trúc: {current_plan.architecture_pattern}
Danh sách file:
{files_overview}

### [NHẬT KÝ LỖI SANDBOX]:
{error_log}

### [CHỈ THỊ SỬA ĐỔI TỪ REVIEWER]:
{reviewer_instructions}

{guidelines}

### [NHIỆM VỤ]:
Hãy điều chỉnh lại kiến trúc, chuẩn hóa lại tên hàm, interface signatures, hoặc thêm/bớt file nếu cần để loại bỏ triệt để mâu thuẫn giữa các file.

Trả về DUY NHẤT một JSON Object hợp lệ của `MultiFilePlan` như sau:
{{
  "target_language": "{current_plan.target_language}",
  "architecture_pattern": "{current_plan.architecture_pattern}",
  "execution_order": ["file1", "file2", ...],
  "files": [ ... ],
  "rationale": "Lý do điều chỉnh kiến trúc"
}}
"""

        response_text = self.call_llm(prompt, format_json=True)
        json_obj = self.extract_json_object(response_text)
        if json_obj and "files" in json_obj:
            try:
                return MultiFilePlan.model_validate(json_obj)
            except Exception:
                pass

        return current_plan
