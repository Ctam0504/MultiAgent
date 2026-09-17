"""
multi_agent_system.agents.reviewer_agent
======================================
Agent Reviewer: Tiếp nhận task, plan, code đa tệp, testcase, cây thư mục và log lỗi Sandbox.
Thẩm định nguyên nhân cốt lõi và phân định chính xác:
- PLANNER: Lỗi Global (mâu thuẫn giữa các file, sai import, lệch interface)
- CODER: Lỗi Local (cú pháp nội bộ trong 1 file, lỗi logic cài đặt thân hàm)
- TESTER: Lỗi Testcase (assert sai kỳ vọng, testcase vi phạm yêu cầu bài toán)
"""

import json
from typing import Dict, Optional, Any
from .base_agent import BaseAgent
from ..schemas import MultiFilePlan, ReviewDecision, ReviewTarget
from .. import config
import re
class ReviewerAgent(BaseAgent):
    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        super().__init__(
            model_name=model_name or config.REVIEWER_MODEL,
            base_url=base_url,
            temperature=0.1
        )

    def review(
        self,
        task_goal: str,
        plan: MultiFilePlan,
        files_dict: Dict[str, str],
        test_cases: str,
        error_msg: str,
        history_feedback: str = ""
    ) -> ReviewDecision:
        """
        Thẩm định log lỗi và phân định trách nhiệm.
        """
        code_overview = ""
        for filepath, content in files_dict.items():
            code_overview += f"\n--- FILE: `{filepath}` ---\n```{plan.target_language}\n{content}\n```\n"

        history_section = f"\n### [LỊCH SỬ THẨM ĐỊNH TRƯỚC ĐÓ]:\n{history_feedback}\n" if history_feedback else ""

        prompt = f"""BẠN LÀ META-LOGIC AUDITOR & ROOT-CAUSE SYSTEM ANALYZER.
Nhiệm vụ: Phân tích sự cố thực thi Sandbox, đối chiếu toàn bộ mã nguồn đa tệp và yêu cầu bài toán,
sau đó PHÁN QUYẾT CHÍNH XÁC AI LÀ NGƯỜI SAI (PLANNER, CODER, hay TESTER).

### [1. YÊU CẦU BÀI TOÁN GỐC (SPECIFICATION)]:
{task_goal}

### [2. KẾ HOẠCH KIẾN TRÚC HIỆN TẠI (PLANNER)]:
Kiến trúc: {plan.architecture_pattern}
Các tệp: {[f.filepath for f in plan.files]}

### [3. TOÀN BỘ MÃ NGUỒN CÁC TỆP (CODER)]:
{code_overview}

### [4. KỊCH BẢN KIỂM THỬ (TESTER)]:
```{plan.target_language}
{test_cases}
```

### [5. NHẬT KÝ LỖI SANDBOX THỰC TẾ]:
{error_msg if error_msg else "Mã nguồn thực thi thành công, không có lỗi runtime."}
{history_section}

### QUY TRÌNH THẨM ĐỊNH VÀ NGUYÊN TẮC PHÂN ĐỊNH TRÁCH NHIỆM:

BƯỚC 1: XÁC ĐỊNH NGUỒN GỐC TỆP BỊ LỖI (FILE TRACING ANALYSIS):
- Đọc kỹ thông báo lỗi trong [5. NHẬT KÝ LỖI SANDBOX THỰC TẾ] để tìm chính xác TÊN TỆP và SỐ DÒNG báo lỗi.
- LƯU Ý PHÂN BIỆT QUAN TRỌNG:
  + Tệp kiểm thử (TESTER): Chỉ bao gồm tệp `TestHarness.java`, `test_harness.py`, `test_harness.c`.
  + Tệp mã nguồn dự án (CODER/PLANNER): Tất cả các tệp trong [3. TOÀN BỘ MÃ NGUỒN CÁC TỆP] (bao gồm `Main.java`, `main.c`, `app.py`, `services/*`, `models/*`, `data/*`, v.v.). Các tệp này là mã nguồn dự án, TUYỆT ĐỐI KHÔNG PHẢI là TestHarness của Tester!

BƯỚC 2: CÂY QUYẾT ĐỊNH PHÂN ĐỊNH TRÁCH NHIỆM (CHỌN DUY NHẤT 1 TARGET):

1. **LỖI BIÊN DỊCH / CÚ PHÁP TẠI TỆP MÃ NGUỒN DỰ ÁN (TUYỆT ĐỐI KHÔNG CHỌN TESTER):**
   - Nếu tệp bị lỗi trong log là tệp mã nguồn của Coder/Planner (ví dụ: `services/MovieService.java:8: error: cannot find symbol`, `data/MovieRepository.java`, `Main.java`):
     -> NGUYÊN TẮC CỐT LÕI: Khi mã nguồn dự án không biên dịch được, TestHarness CHƯA TỪNG ĐƯỢC CHẠY. Do đó lỗi 100% thuộc về CODER hoặc PLANNER, NGHIÊM CẤM ĐỔ LỖI CHO TESTER!
   - Phân định giữa PLANNER và CODER:
     + **PLANNER (GLOBAL)**: Lỗi cấu trúc/kiến trúc đa tệp - thiếu file interface (ví dụ code ghi `implements MovieServiceInterface` nhưng kế hoạch kiến trúc không có file `MovieServiceInterface.java`), sai cấu trúc package/import giữa các module, hoặc lệch chữ ký phương thức giữa hai tầng Service/Repository.
     + **CODER (LOCAL)**: Lỗi cú pháp nội bộ một file, lỗi triển khai thân hàm, sai kiểu dữ liệu, hoặc Coder tự ý khởi tạo interface (`new Repository()`), gọi sai constructor của class nội bộ.

2. **LỖI BIÊN DỊCH TẠI TỆP KIỂM THỬ (TESTHARNESS):**
   - Chỉ áp dụng khi tệp báo lỗi trong log CHÍNH LÀ `TestHarness.java`, `test_harness.py`, `test_harness.c`.
   - Nếu Coder đã viết đúng class/hàm theo đề bài nhưng TestHarness gọi sai kiểu dữ liệu, sai tham số, hoặc import sai -> Chọn **TESTER (TESTCASE)**.
   - Nếu đề bài yêu cầu một hàm/class cụ thể nhưng Coder chưa viết, khiến TestHarness gọi bị lỗi -> Chọn **CODER (LOCAL)**.

3. **LỖI RUNTIME / ASSERTION FAILURE (MÃ CHẠY ĐƯỢC NHƯNG TEST THẤT BẠI):**
   - Áp dụng khi mã nguồn và TestHarness đều biên dịch thành công, nhưng khi thực thi bị Exception hoặc Assert fail.
   - Đối chiếu với [1. YÊU CẦU BÀI TOÁN GỐC]:
     + Nếu Coder tính toán sai thuật toán hoặc không đáp ứng đúng yêu cầu đề bài -> Chọn **CODER (LOCAL)**.
     + Nếu Coder đã làm đúng yêu cầu đề bài nhưng Testcase kiểm tra điều kiện vô lý hoặc sai giá trị kỳ vọng -> Chọn **TESTER (TESTCASE)**.

### ĐỊNH DẠNG TRẢ VỀ:
Trả về DUY NHẤT một JSON Object hợp lệ:
{{
  "status": "REJECTED",
  "target": "PLANNER" | "CODER" | "TESTER",
  "error_category": "GLOBAL" | "LOCAL" | "TESTCASE",
  "failed_file": "tên_file_thực_sự_bị_lỗi_trong_log",
  "root_cause": "nguyên nhân kỹ thuật cốt lõi kèm vị trí file và dòng bị lỗi",
  "instructions": "chỉ thị sửa đổi cụ thể cho target agent",
  "audit_table": "tóm tắt đối chiếu"
}}
"""

        raw_resp = self.call_llm(prompt, format_json=True)
        json_obj = self.extract_json_object(raw_resp)

        if json_obj and "target" in json_obj:
            try:
                target_str = str(json_obj.get("target", "UNKNOWN")).upper().strip()
                if "PLANNER" in target_str:
                    target_enum = ReviewTarget.PLANNER
                    cat = "GLOBAL"
                elif "TESTER" in target_str:
                    target_enum = ReviewTarget.TESTER
                    cat = "TESTCASE"
                elif "PASSED" in target_str:
                    target_enum = ReviewTarget.PASSED
                    cat = "NONE"
                else:
                    target_enum = ReviewTarget.CODER
                    cat = "LOCAL"

                raw_audit = json_obj.get("audit_table", "")
                if isinstance(raw_audit, (dict, list)):
                    audit_table_val = json.dumps(raw_audit, ensure_ascii=False, indent=2)
                else:
                    audit_table_val = str(raw_audit) if raw_audit is not None else ""

                return ReviewDecision(
                    status=str(json_obj.get("status", "REJECTED")),
                    target=target_enum,
                    error_category=str(json_obj.get("error_category", cat)),
                    failed_file=json_obj.get("failed_file"),
                    root_cause=str(json_obj.get("root_cause", "Phát hiện lỗi khi thực thi sandbox.")),
                    instructions=str(json_obj.get("instructions", "Vui lòng kiểm tra và sửa đổi theo log lỗi.")),
                    audit_table=audit_table_val
                )
            except Exception as e:
                print(f"⚠️ [Reviewer] Lỗi cấu trúc JSON sang ReviewDecision: {e}")

        # Fallback regex parsing nếu JSON bị lỗi
        return self._fallback_parse_decision(raw_resp, error_msg)

    def _fallback_parse_decision(self, text: str, error_msg: str) -> ReviewDecision:
        target_enum = ReviewTarget.CODER
        category = "LOCAL"

        text_upper = text.upper()
        if "TARGET: PLANNER" in text_upper or '"PLANNER"' in text_upper or "GLOBAL" in text_upper:
            target_enum = ReviewTarget.PLANNER
            category = "GLOBAL"
        elif "TARGET: TESTER" in text_upper or '"TESTER"' in text_upper or "TESTCASE" in text_upper:
            target_enum = ReviewTarget.TESTER
            category = "TESTCASE"
        elif "PASSED" in text_upper and not error_msg:
            target_enum = ReviewTarget.PASSED
            category = "NONE"

        root_cause = ""
        # 1. Thử trích xuất từ định dạng JSON nếu có
        rc_json = re.search(r'"root_cause"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        if rc_json:
            root_cause = rc_json.group(1).encode('utf-8').decode('unicode-escape', errors='ignore').strip()
        else:
            rc_match = re.search(r"ROOT_CAUSE:?\s*(.*?)(?=\n[A-Z_]+:|$)", text, re.IGNORECASE | re.DOTALL)
            if rc_match:
                root_cause = rc_match.group(1).strip()

        if not root_cause:
            if error_msg:
                # Lấy dòng lỗi chính từ error_msg
                lines = [l.strip() for l in error_msg.splitlines() if l.strip()]
                root_cause = lines[-1] if lines else "Lỗi thực thi sandbox."
            else:
                root_cause = "Không thể phân tích chi tiết lỗi."

        # Làm sạch chuỗi root_cause
        root_cause = re.sub(r'^[\s":*]+', '', root_cause).strip()

        instructions = ""
        ins_json = re.search(r'"instructions"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        if ins_json:
            instructions = ins_json.group(1).encode('utf-8').decode('unicode-escape', errors='ignore').strip()
        else:
            ins_match = re.search(r"INSTRUCTION[S]?:?\s*(.*?)(?=\n[A-Z_]+:|$)", text, re.IGNORECASE | re.DOTALL)
            if ins_match:
                instructions = ins_match.group(1).strip()

        if not instructions:
            instructions = "Vui lòng đối chiếu log lỗi và sửa đổi mã nguồn tương ứng."

        instructions = re.sub(r'^[\s":*]+', '', instructions).strip()

        return ReviewDecision(
            status="PASSED" if target_enum == ReviewTarget.PASSED else "REJECTED",
            target=target_enum,
            error_category=category,
            failed_file=None,
            root_cause=root_cause,
            instructions=instructions,
            audit_table=""
        )
