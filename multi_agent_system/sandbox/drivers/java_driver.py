"""
multi_agent_system.sandbox.drivers.java_driver
=============================================
Driver thực thi đa tệp dành cho ngôn ngữ Java.
Hỗ trợ biên dịch đồng thời tất cả các file trong package và chạy TestHarness.
"""

import os
import re
import glob
from typing import Dict
from .base import BaseMultiFileDriver

class JavaMultiFileDriver(BaseMultiFileDriver):
    def prepare_workspace(
        self, 
        files: Dict[str, str], 
        test_cases: str, 
        host_dir: str, 
        use_docker: bool = False
    ) -> str:
        # 1. Ghi toàn bộ các tệp Java vào thư mục tương ứng
        self.write_files(files, host_dir)

        # 2. Xử lý kịch bản kiểm thử TestHarness.java
        # Tự động tìm tất cả các package từ nội dung các file và đường dẫn thư mục để bổ sung import
        packages = set()
        for rel_path, content in files.items():
            # Tìm khai báo package trong nội dung file
            pkg_matches = re.findall(r"^\s*package\s+([a-zA-Z0-9_.]+)\s*;", content, flags=re.MULTILINE)
            for pkg in pkg_matches:
                packages.add(pkg.strip())
            # Tìm package từ cấu trúc thư mục
            rel_dir = os.path.dirname(rel_path).replace("\\", "/").strip("/")
            if rel_dir:
                packages.add(rel_dir.replace("/", "."))

        auto_imports = "\n".join([f"import {pkg}.*;" for pkg in sorted(packages)])

        cleaned_test = test_cases.strip()
        # Loại bỏ các khai báo package (vì TestHarness.java nằm tại root của workspace / default package)
        cleaned_test = re.sub(r"^\s*package\s+[^;]+;\s*", "", cleaned_test, flags=re.MULTILINE)

        if "class TestHarness" in cleaned_test:
            # Tester đã viết đầy đủ class TestHarness
            if auto_imports:
                final_code = f"{auto_imports}\n\n{cleaned_test}"
            else:
                final_code = cleaned_test
        else:
            # Tester chỉ viết các câu lệnh test hoặc method
            import_lines = []
            body_lines = []
            for line in cleaned_test.splitlines():
                if line.strip().startswith("import "):
                    import_lines.append(line.strip())
                else:
                    body_lines.append(line)

            user_imports = "\n".join(import_lines)
            body_code = "\n".join(body_lines)

            final_code = f"""{auto_imports}
{user_imports}

public class TestHarness {{
    public static void main(String[] args) {{
        try {{
            System.out.println("[TEST HARNESS] Starting Java multi-file verification...");
            {body_code}
            System.out.println("[SUCCESS] ALL TEST CASES PASSED");
        }} catch (Throwable e) {{
            System.err.println("[TEST FAILURE]: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }}
    }}
}}
"""
        harness_path = os.path.join(host_dir, "TestHarness.java")
        with open(harness_path, "w", encoding="utf-8") as f:
            f.write(final_code)

        # 3. Phân tách danh sách file mã nguồn dự án (Coder) và file TestHarness (Tester)
        # Thực hiện cơ chế kiểm thử 2 giai đoạn (2-Phase Verification):
        # Giai đoạn 1: Biên dịch toàn bộ mã nguồn dự án trước. Nếu lỗi -> 100% lỗi do Coder/Planner.
        # Giai đoạn 2: Chỉ khi mã nguồn biên dịch thành công mới biên dịch và chạy TestHarness.
        java_files = glob.glob(os.path.join(host_dir, "**", "*.java"), recursive=True)
        harness_abs = os.path.abspath(harness_path)
        project_java_files = [jf for jf in java_files if os.path.abspath(jf) != harness_abs]

        project_sources_file = os.path.join(host_dir, "project_sources.txt")
        with open(project_sources_file, "w", encoding="utf-8") as f:
            for jf in project_java_files:
                rel_j = os.path.relpath(jf, host_dir).replace("\\", "/")
                f.write(f'"{rel_j}"\n')

        if project_java_files:
            if use_docker:
                return (
                    "sh -c 'javac -d /workspace @/workspace/project_sources.txt && "
                    "javac -d /workspace -cp /workspace /workspace/TestHarness.java && "
                    "java -cp /workspace TestHarness'"
                )
            # Local execution (Windows / Linux)
            return "javac -d . @project_sources.txt && javac -cp . TestHarness.java && java -cp . TestHarness"
        else:
            if use_docker:
                return "sh -c 'javac -d /workspace /workspace/TestHarness.java && java -cp /workspace TestHarness'"
            return "javac -cp . TestHarness.java && java -cp . TestHarness"
