import os
import glob
import networkx as nx
from typing import Tuple, List, Dict, Any
from pydantic import BaseModel

# Tree-sitter core engine + Grammar packages
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_java as tsjava

# Import model CodeChunk của bạn (hoặc dùng Pydantic bên dưới nếu chưa có)
try:
    from models.code_models import CodeChunk
except ImportError:
    class CodeChunk(BaseModel):
        id: str
        type: str
        file_path: str
        content: str


class UnifiedTreeSitterGraphExtractor:
    """
    Parser đa ngôn ngữ (Python & Java) dùng chung một Engine Tree-sitter.
    Trích xuất Knowledge Graph chuẩn hóa (DEFINES, IMPORTS, INHERITS, CALLS).
    """
    def __init__(self, filename: str, code_bytes: bytes, language_type: str, graph: nx.DiGraph):
        self.filename = filename
        self.code_bytes = code_bytes
        self.language_type = language_type.lower()  # 'python' hoặc 'java'
        self.graph = graph

        # Khởi tạo Grammar tương ứng
        if self.language_type == "python":
            self.lang = Language(tspython.language())
        elif self.language_type == "java":
            self.lang = Language(tsjava.language())
        else:
            raise ValueError(f"Ngôn ngữ {language_type} chưa được hỗ trợ.")

        self.parser = Parser(self.lang)
        self.tree = self.parser.parse(self.code_bytes)

        self.file_node_id = f"file:{filename}"
        self.graph.add_node(self.file_node_id, type="file", path=filename, lang=self.language_type)

    def _get_node_text(self, node) -> str:
        """Đọc chuỗi string từ byte array dựa trên vị trí node."""
        if not node:
            return ""
        return self.code_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

    def extract(self):
        """Khởi chạy duyệt cây AST đa ngôn ngữ."""
        root = self.tree.root_node
        self._traverse(root, current_class_id=None)

    def _traverse(self, node, current_class_id: str = None):
        # ==========================================
        # 1. TRÍCH XUẤT IMPORTS / PACKAGES
        # ==========================================
        import_types = ["import_statement", "import_from_statement"] if self.language_type == "python" else ["import_declaration"]
        if node.type in import_types:
            import_text = self._get_node_text(node).replace("import", "").replace(";", "").strip()
            imp_id = f"import:{import_text}"
            self.graph.add_node(imp_id, type="import", name=import_text)
            self.graph.add_edge(self.file_node_id, imp_id, relation="IMPORTS")

        # ==========================================
        # 2. TRÍCH XUẤT CLASS / INTERFACE DEFINITION
        # ==========================================
        class_types = ["class_definition"] if self.language_type == "python" else ["class_declaration", "interface_declaration", "enum_declaration"]
        if node.type in class_types:
            name_node = node.child_by_field_name("name")
            if name_node:
                class_name = self._get_node_text(name_node)
                class_node_id = f"class:{self.filename}:{class_name}"

                # Lấy danh sách Class cha / Interface
                bases = []
                if self.language_type == "python":
                    superclasses_node = node.child_by_field_name("superclasses")
                    if superclasses_node:
                        for child in superclasses_node.children:
                            if child.type in ["identifier", "attribute"]:
                                bases.append(self._get_node_text(child))
                else:  # Java
                    super_class_node = node.child_by_field_name("superclass")
                    if super_class_node:
                        bases.append(self._get_node_text(super_class_node).replace("extends", "").strip())
                    interfaces_node = node.child_by_field_name("interfaces")
                    if interfaces_node:
                        interfaces_text = self._get_node_text(interfaces_node).replace("implements", "").strip()
                        bases.extend([i.strip() for i in interfaces_text.split(",") if i.strip()])

                self.graph.add_node(
                    class_node_id,
                    type="class",
                    name=class_name,
                    file=self.filename,
                    lang=self.language_type,
                    bases=",".join(bases)
                )
                self.graph.add_edge(self.file_node_id, class_node_id, relation="DEFINES")

                for base in bases:
                    self.graph.add_edge(class_node_id, f"class_ref:{base}", relation="INHERITS")

                # Đệ quy vào thân Class
                body_node = node.child_by_field_name("body")
                if body_node:
                    for child in body_node.children:
                        self._traverse(child, current_class_id=class_node_id)
                return

        # ==========================================
        # 3. TRÍCH XUẤT FUNCTION / METHOD / CONSTRUCTOR
        # ==========================================
        func_types = ["function_definition", "async_function_definition"] if self.language_type == "python" else ["method_declaration", "constructor_declaration"]
        if node.type in func_types:
            name_node = node.child_by_field_name("name")
            func_name = self._get_node_text(name_node) if name_node else "<init>"
            func_code = self._get_node_text(node)

            params_node = node.child_by_field_name("parameters")
            args_str = self._get_node_text(params_node) if params_node else "()"

            if current_class_id:
                func_node_id = f"method:{current_class_id}:{func_name}"
                parent_id = current_class_id
                node_type = "method"
            else:
                func_node_id = f"func:{self.filename}:{func_name}"
                parent_id = self.file_node_id
                node_type = "function"

            self.graph.add_node(
                func_node_id,
                type=node_type,
                name=func_name,
                file=self.filename,
                lang=self.language_type,
                args=args_str,
                code=func_code
            )
            self.graph.add_edge(parent_id, func_node_id, relation="DEFINES")

            # Quét lời gọi hàm (CALLS)
            called_funcs = self._extract_calls(node)
            for called_func in called_funcs:
                self.graph.add_edge(func_node_id, f"call_ref:{called_func}", relation="CALLS")
            return

        # Đệ quy xuống các node con khác
        for child in node.children:
            self._traverse(child, current_class_id=current_class_id)

    def _extract_calls(self, func_node) -> List[str]:
        """Quét tất cả các lời gọi hàm/phương thức bên trong hàm (Hoạt động cho cả Python & Java)."""
        calls = []
        stack = [func_node]
        target_type = "call" if self.language_type == "python" else "method_invocation"

        while stack:
            curr = stack.pop()
            if curr.type == target_type:
                if self.language_type == "python":
                    function_node = curr.child_by_field_name("function")
                    if function_node:
                        if function_node.type == "identifier":
                            calls.append(self._get_node_text(function_node))
                        elif function_node.type == "attribute":
                            attr_node = function_node.child_by_field_name("attribute")
                            if attr_node:
                                calls.append(self._get_node_text(attr_node))
                else:  # Java
                    name_node = curr.child_by_field_name("name")
                    if name_node:
                        calls.append(self._get_node_text(name_node))

            stack.extend(curr.children)
        return calls


# ==========================================
# MAIN FUNCTION DÙNG CHUNG CHO CẢ CODEBASE
# ==========================================

def parse_codebase_to_graph_and_chunks(source_dir: str) -> Tuple[nx.DiGraph, List[CodeChunk]]:
    """
    Quét tự động toàn bộ codebase (bao gồm .py và .java),
    xây dựng Knowledge Graph và Vector Chunks thống nhất.
    """
    graph = nx.DiGraph()

    # Quét tất cả file Python và Java
    py_files = glob.glob(os.path.join(source_dir, "**", "*.py"), recursive=True)
    java_files = glob.glob(os.path.join(source_dir, "**", "*.java"), recursive=True)
    all_files = [(f, "python") for f in py_files] + [(f, "java") for f in java_files]

    print(f"🔍 [Unified Extractor] Tìm thấy {len(py_files)} file Python và {len(java_files)} file Java.")

    for file_path, lang in all_files:
        rel_path = os.path.relpath(file_path, source_dir)
        try:
            with open(file_path, "rb") as f:
                code_bytes = f.read()

            extractor = UnifiedTreeSitterGraphExtractor(
                filename=rel_path,
                code_bytes=code_bytes,
                language_type=lang,
                graph=graph
            )
            extractor.extract()

        except Exception as e:
            print(f"❌ Lỗi parse file ({lang}) {rel_path}: {e}")

    # Tạo Chunks cho Vector DB (Giữ nguyên cấu trúc Schema cũ)
    chunks: List[CodeChunk] = []
    for node_id, data in graph.nodes(data=True):
        node_type = data.get("type", "")
        lang = data.get("lang", "python")

        if node_type == "class":
            neighbors = list(graph.successors(node_id))
            methods = [graph.nodes[n].get("name", "") for n in neighbors if graph.nodes[n].get("type") == "method"]
            content = f"Language: {lang.upper()}\nFile: {data['file']}\nClass: {data['name']}\nBases: {data.get('bases', '')}\nMethods: {', '.join(methods)}"

        elif node_type in ["function", "method"]:
            out_edges = graph.out_edges(node_id, data=True)
            called_funcs = [target.replace("call_ref:", "") for _, target, d in out_edges if d.get("relation") == "CALLS"]
            content = f"Language: {lang.upper()}\nFile: {data['file']}\nFunction: {data['name']}{data.get('args','')}\nCalls: {', '.join(called_funcs)}\nCode:\n```{lang}\n{data.get('code','')}\n```"

        else:
            continue

        chunks.append(CodeChunk(
            id=node_id,
            type=node_type,
            file_path=data.get("file", ""),
            content=content
        ))

    print(f"✅ [Unified Extractor] Đã tạo thành công {graph.number_of_nodes()} Nodes và {len(chunks)} Chunks!")
    return graph, chunks