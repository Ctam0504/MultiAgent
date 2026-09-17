import os
import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import ollama

# ==========================================
# 1. STRUCTURED SCHEMAS (Pydantic Models)
# ==========================================

class FileSpec(BaseModel):
    filepath: str = Field(description="Đường dẫn tương đối của file bao gồm cả phần mở rộng (.py, .java, .c, .h)")
    action: str = Field(description="CREATE hoặc MODIFY")
    dependencies: List[str] = Field(default_factory=list, description="Danh sách các filepath mà file này phụ thuộc vào")
    purpose: str = Field(description="Mục đích và trách nhiệm của tệp này")
    interface_summary: str = Field(description="Chi tiết các Class, Function Signatures, Structs hoặc Header definitions")

class MultiFilePlan(BaseModel):
    architecture_pattern: str = Field(description="Mẫu kiến trúc phần mềm sử dụng")
    execution_order: List[str] = Field(description="Danh sách các `filepath` xếp theo thứ tự sinh từ Leaf đến Root node")
    files: List[FileSpec]

# ==========================================
# 2. LOCAL MULTI-LANGUAGE AGENT ENGINE
# ==========================================

class LocalMultiFileGenerator:
    def __init__(self, workspace_dir: str, model_name: str = "qwen2.5-coder:7b", target_language: str = "python"):
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.model_name = model_name
        self.target_language = target_language.lower()
        os.makedirs(self.workspace_dir, exist_ok=True)

    def _get_language_rules(self) -> str:
        """Định nghĩa quy tắc cấu trúc file và import theo từng ngôn ngữ."""
        if self.target_language == "java":
            return """
QUY TẮC BẮT BUỘC DÀNH CHO JAVA:
1. Mọi `filepath` phải có đuôi `.java` và tuân thủ chuẩn cấu trúc Java package (ví dụ: `models/TextChunk.java`, `services/EmbeddingService.java`).
2. Tên Class trong code PHẢI TRÙNG KHỚP 100% với tên file `.java`.
3. Khai báo `package` ở đầu mỗi file phù hợp với đường dẫn thư mục.
4. Đảm bảo import đúng giữa các package.
"""
        elif self.target_language in ["c", "cpp"]:
            return """
QUY TẮC BẮT BUỘC DÀNH CHO C/C++:
1. Tạo đầy đủ các file Header (`.h`) cho interface/structs và file nguồn (`.c`/`.cpp`) cho logic implementation.
2. File Header PHẢI có Include Guards (`#ifndef... #define... #endif`).
3. Sử dụng `#include "relative_path/file.h"` để liên kết giữa các module.
4. Tách biệt rõ ràng giữa khai báo (Header) và triển khai (Source code).
"""
        else:  # python
            return """
QUY TẮC BẮT BUỘC DÀNH CHO PYTHON:
1. Tất cả `filepath` phải có đuôi `.py`.
2. Dùng absolute/relative import chuẩn xác dựa trên cấu trúc các tệp đã tạo.
"""

    def run_planner_agent(self, user_prompt: str) -> MultiFilePlan:
        lang_rules = self._get_language_rules()
        
        planner_prompt = f"""
Bạn là một System Architect Agent chuyên nghiệp.
Nhiệm vụ: Phân tích yêu cầu và lập kế hoạch cấu trúc ĐA TỆP cho ngôn ngữ lập trình: **{self.target_language.upper()}**.

QUY TẮC BẮT BUỘC:
1. Thiết kế kiến trúc sạch (Modular / Clean Architecture) phù hợp với {self.target_language.upper()}.
2. Chuỗi trong mảng `execution_order` PHẢI KHỚP KHÔNG SAI MỘT KÝ TỰ với `filepath` trong `files`.
3. Sắp xếp `execution_order` theo Topo: File độc lập (Data Models/Headers) đứng trước, file phụ thuộc đứng sau, file khởi chạy chính (Main/App) đứng cuối cùng.

{lang_rules}

Yêu cầu bài toán: {user_prompt}
"""

        print(f" -> Planner đang suy luận kế hoạch kiến trúc [{self.target_language.upper()}]...")
        
        response = ollama.chat(
            model=self.model_name,
            messages=[{'role': 'user', 'content': planner_prompt}],
            format=MultiFilePlan.model_json_schema(),
            options={'temperature': 0.1}
        )

        return MultiFilePlan.model_validate_json(response['message']['content'])

    def run_coder_agent(self, file_spec: FileSpec, created_files_context: Dict[str, str]) -> str:
        context_str = ""
        for dep in file_spec.dependencies:
            if dep in created_files_context:
                context_str += f"\n--- NGỮ CẢNH TỆP PHỤ THUỘ `{dep}` ---\n{created_files_context[dep]}\n"

        existing_files = list(created_files_context.keys())
        lang_rules = self._get_language_rules()

        coder_prompt = f"""
Bạn là một Senior Software Engineer chuyên về **{self.target_language.upper()}**.
Nhiệm vụ: Viết mã nguồn HOÀN CHỈNH cho tệp: `{file_spec.filepath}`.

- Mục đích tệp: {file_spec.purpose}
- Interface yêu cầu: {file_spec.interface_summary}
- Các file phụ thuộc được khai báo: {file_spec.dependencies}

DANH SÁCH CÁC TỆP NỀN TẢNG ĐÃ TỒN TẠI TRONG WORKSPACE:
{existing_files}

{context_str}

{lang_rules}

QUY TẮC CHUNG:
1. Chỉ trả về mã nguồn {self.target_language.upper()} chuẩn xác. KHÔNG giải thích, KHÔNG bọc trong markdown codeblock.
2. Tái sử dụng chính xác tên Class, Struct, Function, Parameter từ các tệp phụ thuộc ở trên.
3. Viết code đầy đủ logic, xử lý lỗi hợp lý, KHÔNG chèn comment TODO hay placeholder.
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{'role': 'user', 'content': coder_prompt}],
            options={'temperature': 0.1}
        )

        clean_code = response['message']['content'].strip()
        # Clean markdown wrappers nếu LLM vô tình trả về
        if clean_code.startswith("```"):
            lines = clean_code.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            clean_code = "\n".join(lines).strip()

        return clean_code

    def execute_generation(self, user_prompt: str) -> MultiFilePlan:
        print(f"=== [STEP 1] KHỞI CHẠY LOCAL PLANNER AGENT ({self.target_language.upper()}) ===")
        plan = self.run_planner_agent(user_prompt)
        print(f" -> Mẫu kiến trúc: {plan.architecture_pattern}")

        actual_filepaths = [f.filepath for f in plan.files]
        valid_execution_order = [fp for fp in plan.execution_order if fp in actual_filepaths]
        
        if not valid_execution_order:
            valid_execution_order = actual_filepaths

        print(f" -> Thứ tự sinh file thực tế: {valid_execution_order}\n")

        created_files_context: Dict[str, str] = {}
        spec_map = {f.filepath: f for f in plan.files}

        print(f"=== [STEP 2] KHỞI CHẠY LOCAL CODER AGENT ({self.target_language.upper()}) ===")
        for filepath in valid_execution_order:
            if filepath not in spec_map:
                continue
            
            spec = spec_map[filepath]
            print(f" -> Coder đang sinh tệp: {filepath}...")
            
            code = self.run_coder_agent(spec, created_files_context)
            created_files_context[filepath] = code
            
            full_path = os.path.join(self.workspace_dir, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(code)
                
            print(f"    PASSED: Đã lưu {filepath}")

        print(f"\n=== HOÀN THÀNH: Đã tạo xong dự án {self.target_language.upper()} tại local workspace! ===")
        return plan

# ==========================================
# 3. CHẠY THỬ NGHIỆM DỰ ÁN MULTI-LANGUAGE
# ==========================================
if __name__ == "__main__":
    PROMPT = """
    Xây dựng module RAG (Retrieval-Augmented Generation) tìm kiếm ngữ nghĩa văn bản:
    - Text Processor: Đọc văn bản, làm sạch và thực hiện Chunking (tách nhỏ văn bản).
    - Embedding Service: Tính toán Vector Embedding cho các đoạn văn bản (mock vector 128-dim).
    - Vector Store: Quản lý lưu trữ vector và tính toán độ tương đồng Cosine Similarity để tìm K kết quả liên quan nhất.
    - RAG Pipeline: Bộ điều phối nhận câu hỏi người dùng, truy vấn Vector Store và tổng hợp thành context hoàn chỉnh.
    """

    # --- Ví dụ 1: Sinh codebase C ---
    c_generator = LocalMultiFileGenerator(
        workspace_dir="./local_python_workspace", 
        model_name="qwen2.5-coder:7b",
        target_language="python"
    )
    c_generator.execute_generation(PROMPT)

    # --- Ví dụ 2: Sinh codebase Java ---
    # java_generator = LocalMultiFileGenerator(
    #     workspace_dir="./local_java_workspace", 
    #     model_name="qwen2.5-coder:7b",
    #     target_language="java"
    # )
    # java_generator.execute_generation(PROMPT)