import os
import glob
import networkx as nx
from typing import Tuple, List, Dict, Any
from pydantic import BaseModel

from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_java as tsjava
import tree_sitter_c as tsc

try:
    from models.code_models import CodeChunk
except ImportError:
    class CodeChunk(BaseModel):
        id: str
        type: str
        file_path: str
        content: str


class UnifiedTreeSitterGraphExtractor:
    def __init__(self, filename: str, code_bytes: bytes, language_type: str, graph: nx.DiGraph):
        self.filename = filename
        self.code_bytes = code_bytes
        self.language_type = language_type.lower()
        self.graph = graph

        # SỬA LỖI 1: Cập nhật API tương thích Tree-Sitter >= 0.22.0
        if self.language_type == "python":
            self.lang = Language(tspython.language())
        elif self.language_type == "java":
            self.lang = Language(tsjava.language())
        elif self.language_type in ["c", "cpp"]:
            self.lang = Language(tsc.language())
        else:
            raise ValueError(f"Ngôn ngữ {language_type} chưa được hỗ trợ.")

        self.parser = Parser()
        self.parser.language = self.lang
        self.tree = self.parser.parse(self.code_bytes)

        self.file_node_id = f"file:{filename}"
        self.graph.add_node(self.file_node_id, type="file", path=filename, lang=self.language_type)

    def _get_node_text(self, node) -> str:
        if not node:
            return ""
        return self.code_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

    def extract(self):
        root = self.tree.root_node
        self._traverse(root, current_struct_id=None)

    def _get_c_function_name(self, func_node) -> str:
        """Trích xuất tên hàm trong C bằng đệ quy tìm identifier trong declarator."""
        declarator = func_node.child_by_field_name("declarator")
        
        def find_identifier(node) -> str:
            if not node:
                return ""
            if node.type == "identifier":
                return self._get_node_text(node)
            for child in node.children:
                res = find_identifier(child)
                if res:
                    return res
            return ""

        func_name = find_identifier(declarator)
        return func_name if func_name else "unknown_func"

    def _traverse(self, node, current_struct_id: str = None):
        # 1. IMPORTS / INCLUDES
        if self.language_type == "python":
            import_types = ["import_statement", "import_from_statement"]
        elif self.language_type == "java":
            import_types = ["import_declaration"]
        else:
            import_types = ["preproc_include"]

        if node.type in import_types:
            if self.language_type in ["c", "cpp"]:
                path_node = node.child_by_field_name("path")
                import_text = self._get_node_text(path_node).strip('"<>') if path_node else self._get_node_text(node)
            else:
                import_text = self._get_node_text(node).replace("import", "").replace(";", "").strip()

            imp_id = f"import:{import_text}"
            self.graph.add_node(imp_id, type="import", name=import_text)
            self.graph.add_edge(self.file_node_id, imp_id, relation="IMPORTS")

        # 2. CLASS / STRUCT / UNION
        if self.language_type == "python":
            struct_types = ["class_definition"]
        elif self.language_type == "java":
            struct_types = ["class_declaration", "interface_declaration", "enum_declaration"]
        else:
            struct_types = ["struct_specifier", "union_specifier", "enum_specifier"]

        if node.type in struct_types:
            name_node = node.child_by_field_name("name")
            struct_name = self._get_node_text(name_node) if name_node else "<anonymous_struct>"
            
            if struct_name != "<anonymous_struct>" or node.child_by_field_name("body"):
                struct_node_id = f"struct:{self.filename}:{struct_name}"
                bases = []
                if self.language_type == "python":
                    superclasses_node = node.child_by_field_name("superclasses")
                    if superclasses_node:
                        for child in superclasses_node.children:
                            if child.type in ["identifier", "attribute"]:
                                bases.append(self._get_node_text(child))
                elif self.language_type == "java":
                    super_class_node = node.child_by_field_name("superclass")
                    if super_class_node:
                        bases.append(self._get_node_text(super_class_node).replace("extends", "").strip())

                self.graph.add_node(
                    struct_node_id,
                    type="struct" if self.language_type in ["c", "cpp"] else "class",
                    name=struct_name,
                    file=self.filename,
                    lang=self.language_type,
                    bases=",".join(bases)
                )
                self.graph.add_edge(self.file_node_id, struct_node_id, relation="DEFINES")

                body_node = node.child_by_field_name("body")
                if body_node:
                    for child in body_node.children:
                        self._traverse(child, current_struct_id=struct_node_id)
                return

        # 3. FUNCTION / METHOD
        if self.language_type == "python":
            func_types = ["function_definition", "async_function_definition"]
        elif self.language_type == "java":
            func_types = ["method_declaration", "constructor_declaration"]
        else:
            func_types = ["function_definition"]

        if node.type in func_types:
            if self.language_type in ["c", "cpp"]:
                func_name = self._get_c_function_name(node)
            else:
                name_node = node.child_by_field_name("name")
                func_name = self._get_node_text(name_node) if name_node else "<init>"

            func_code = self._get_node_text(node)
            params_node = node.child_by_field_name("parameters")
            args_str = self._get_node_text(params_node) if params_node else "()"

            # SỬA LỖI 2 & 4: Tạo Node ID duy nhất kết hợp Line Number & Gắn liên kết Class nếu có
            start_line = node.start_point[0] + 1
            func_node_id = f"func:{self.filename}:{struct_prefix if (struct_prefix := current_struct_id.split(':')[-1] + '.' if current_struct_id else '') else ''}{func_name}:{start_line}"
            
            self.graph.add_node(
                func_node_id,
                type="function" if not current_struct_id else "method",
                name=func_name,
                file=self.filename,
                lang=self.language_type,
                args=args_str,
                code=func_code
            )

            # Nối từ Struct/Class nếu là Method, hoặc nối từ File nếu là Hàm tự do
            if current_struct_id:
                self.graph.add_edge(current_struct_id, func_node_id, relation="HAS_METHOD")
            self.graph.add_edge(self.file_node_id, func_node_id, relation="DEFINES")

            called_funcs = self._extract_calls(node)
            for called_func in called_funcs:
                self.graph.add_edge(func_node_id, f"call_ref:{called_func}", relation="CALLS")
            return

        # Đệ quy xuống các node con
        for child in node.children:
            self._traverse(child, current_struct_id=current_struct_id)

    def _extract_calls(self, func_node) -> List[str]:
        calls = []
        stack = [func_node]

        if self.language_type == "python":
            target_type = "call"
        elif self.language_type == "java":
            target_type = "method_invocation"
        else:
            target_type = "call_expression"

        while stack:
            curr = stack.pop()
            if curr.type == target_type:
                if self.language_type == "python":
                    function_node = curr.child_by_field_name("function")
                    if function_node:
                        # SỬA LỖI 3: Lấy toàn bộ tên hàm/thuộc tính gọi
                        calls.append(self._get_node_text(function_node))
                elif self.language_type == "java":
                    name_node = curr.child_by_field_name("name")
                    if name_node:
                        calls.append(self._get_node_text(name_node))
                else:
                    function_node = curr.child_by_field_name("function")
                    if function_node:
                        calls.append(self._get_node_text(function_node))

            stack.extend(curr.children)
        return calls


def parse_codebase_to_graph_and_chunks(source_dir: str) -> Tuple[nx.DiGraph, List[CodeChunk]]:
    graph = nx.DiGraph()

    py_files = glob.glob(os.path.join(source_dir, "**", "*.py"), recursive=True)
    java_files = glob.glob(os.path.join(source_dir, "**", "*.java"), recursive=True)
    c_files = glob.glob(os.path.join(source_dir, "**", "*.c"), recursive=True)
    h_files = glob.glob(os.path.join(source_dir, "**", "*.h"), recursive=True)

    all_files = (
        [(f, "python") for f in py_files] +
        [(f, "java") for f in java_files] +
        [(f, "c") for f in c_files + h_files]
    )

    print(f"🔍 [Unified Extractor] Tìm thấy {len(py_files)} Python, {len(java_files)} Java, {len(c_files) + len(h_files)} C/Header files.")

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

    chunks: List[CodeChunk] = []
    for node_id, data in graph.nodes(data=True):
        node_type = data.get("type", "")
        lang = data.get("lang", "python")

        if node_type in ["class", "struct"]:
            content = f"Language: {lang.upper()}\nFile: {data['file']}\n{node_type.capitalize()}: {data['name']}\nBases: {data.get('bases', '')}"
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