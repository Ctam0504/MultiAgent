import os
import shutil
import tempfile
import textwrap
import ast
import networkx as nx
import chromadb
from typing import List, Set, Tuple
import config
from storage.db_manager import get_embeddings, ollama_client, build_vector_and_graph_db
from extractors.ast_extractor import parse_codebase_to_graph_and_chunks
from pipeline.rag_pipeline import expand_nodes_via_graph

def self_heal_python(code: str) -> str:
    """
    Tự động sửa lỗi cú pháp phổ biến trong các đoạn code snippet để ast.parse có thể chạy được.
    """
    code = textwrap.dedent(code)
    
    brackets = {'(': ')', '[': ']', '{': '}'}
    stack = []
    in_single_quote = False
    in_double_quote = False
    in_triple_double = False
    in_triple_single = False
    
    i = 0
    while i < len(code):
        char = code[i]
        if code[i:i+3] == '"""':
            in_triple_double = not in_triple_double
            i += 3
            continue
        elif code[i:i+3] == "'''":
            in_triple_single = not in_triple_single
            i += 3
            continue
            
        if in_triple_double or in_triple_single:
            i += 1
            continue
            
        if char == '"' and (i == 0 or code[i-1] != '\\'):
            in_double_quote = not in_double_quote
        elif char == "'" and (i == 0 or code[i-1] != '\\'):
            in_single_quote = not in_single_quote
            
        if in_double_quote or in_single_quote:
            i += 1
            continue
            
        if char in brackets:
            stack.append(char)
        elif char in brackets.values():
            if stack and brackets[stack[-1]] == char:
                stack.pop()
        i += 1
        
    while stack:
        opening = stack.pop()
        code += brackets[opening]
        
    lines = code.splitlines()
    for attempt in range(50):
        current_code = "\n".join(lines)
        try:
            ast.parse(current_code)
            return current_code
        except SyntaxError as e:
            err_line = e.lineno
            if err_line is None:
                break
                
            idx = err_line - 1
            if idx >= len(lines):
                idx = len(lines) - 1
                
            if "expected an indented block" in str(e) or "expected ':'" in str(e):
                curr_line = lines[idx]
                indent = len(curr_line) - len(curr_line.lstrip())
                lines.insert(idx + 1, " " * (indent + 4) + "pass")
            else:
                lines[idx] = "pass"
                
    wrapped_lines = ["def dummy_wrapper_func():"]
    for line in code.splitlines():
        wrapped_lines.append("    " + line)
        
    for attempt in range(50):
        current_code = "\n".join(wrapped_lines)
        try:
            ast.parse(current_code)
            return current_code
        except SyntaxError as e:
            err_line = e.lineno
            if err_line is None:
                break
            idx = err_line - 1
            if idx >= len(wrapped_lines):
                idx = len(wrapped_lines) - 1
                
            if "expected an indented block" in str(e) or "expected ':'" in str(e):
                curr_line = wrapped_lines[idx]
                indent = len(curr_line) - len(curr_line.lstrip())
                wrapped_lines.insert(idx + 1, " " * (indent + 4) + "pass")
            else:
                wrapped_lines[idx] = "    pass"
                
    return "# Syntax healed failed"


def reconstruct_temp_codebase(file_path: str, prompt: str, right_context: str, crossfile_list: list, temp_dir: str, groundtruth: str = ""):
    """
    Dựng cấu trúc thư mục codebase tạm thời từ prompt (file hiện tại) và crossfile_list.
    """
    target_file_full_path = os.path.join(temp_dir, file_path)
    os.makedirs(os.path.dirname(target_file_full_path), exist_ok=True)
    
    full_content = prompt + groundtruth + right_context
    healed_content = self_heal_python(full_content)
    with open(target_file_full_path, "w", encoding="utf-8") as f:
        f.write(healed_content)
        
    for item in crossfile_list:
        filename = item.get("filename")
        chunk = item.get("retrieved_chunk")
        if not filename or not chunk:
            continue
        
        full_path = os.path.join(temp_dir, filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        healed_chunk = self_heal_python(chunk)
        
        mode = "a" if os.path.exists(full_path) else "w"
        with open(full_path, mode, encoding="utf-8") as f:
            if mode == "a":
                f.write("\n\n")
            f.write(healed_chunk)


async def retrieve_context(query: str, db_dir: str, collection_name: str, graph_path: str, top_k: int = 2) -> str:
    """
    Duyệt Đồ thị tri thức và ChromaDB để lấy các đoạn context liên quan (không gọi LLM).
    """
    chroma_client = chromadb.PersistentClient(path=db_dir)
    collection = chroma_client.get_collection(name=collection_name)
    
    if os.path.exists(graph_path) and os.path.getsize(graph_path) > 0:
        graph = nx.read_gml(graph_path)
    else:
        graph = nx.DiGraph()

    if collection.count() > 0:
        query_embedding = (await get_embeddings([query]))[0]
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        seed_node_ids = results["ids"][0]
    else:
        seed_node_ids = []
    
    all_related_node_ids = expand_nodes_via_graph(graph, seed_node_ids)

    retrieved_chunks = []
    for nid in all_related_node_ids:
        if collection.count() > 0:
            doc = collection.get(ids=[nid])
            if doc and doc["documents"]:
                retrieved_chunks.append(doc["documents"][0])
                continue
                
        if graph.has_node(nid):
            ndata = graph.nodes[nid]
            retrieved_chunks.append(f"Graph Connection Node: {nid} (Type: {ndata.get('type', 'ref')})")

    context_str = "\n\n---\n\n".join(retrieved_chunks)
    return context_str


async def run_planner_agent(file_path: str, prompt: str, right_context: str, retrieved_context: str) -> str:
    """
    Planner Agent: Nhận context và code để lập kế hoạch hoàn thành code.
    """
    prompt_text = f"""Bạn là một chuyên gia thiết kế và lập kế hoạch viết code Python.
Nhiệm vụ của bạn là phân tích code hiện tại, cấu trúc đồ thị codebase (GraphRAG context) và lập kế hoạch ngắn gọn, chính xác để điền tiếp phần code bị thiếu ở vị trí cuối của `Prompt Code`.

[TARGET FILE PATH]
{file_path}

[PROMPT CODE (Code phía trước vị trí cần điền)]
```python
{prompt}
```

[RIGHT CONTEXT (Code phía sau vị trí cần điền)]
```python
{right_context}
```

[GRAPH RETRIEVED CONTEXT (Đồ thị codebase & các file liên quan)]
{retrieved_context}

[LƯU Ý CỰC KỲ QUAN TRỌNG VỀ ĐỊNH DẠNG]
- Hãy nhìn kỹ dòng cuối cùng của `Prompt Code`. Nó thường kết thúc lửng lơ ở giữa dòng (ví dụ: kết thúc bằng dấu chấm `.`, ngoặc mở `(`, hoặc toán tử).
- Nhiệm vụ của bạn là lập kế hoạch để hoàn thành dòng lửng lơ đó trước tiên, sao cho khớp với cấu trúc cú pháp và logic của toàn bộ đoạn code cũng như `Right Context`.
- Hãy chỉ ra rõ ràng dòng cuối cùng của `Prompt Code` cần được điền tiếp như thế nào để hoàn thiện.

[YÊU CẦU LẬP KẾ HOẠCH]
Hãy đưa ra một kế hoạch ngắn gọn (1-2 câu tiếng Việt) mô tả:
1. Phần còn thiếu ngay sau dòng cuối cùng của `Prompt Code` cần gọi thuộc tính/hàm nào, hoặc truyền tham số nào của đối tượng nào?
2. Dựa trên các class/hàm tìm được trong GraphRAG context, dòng code hoàn chỉnh đó cần có cú pháp như thế nào?
"""

    response = await ollama_client.chat(
        model=config.MODEL_LLM,
        messages=[{"role": "user", "content": prompt_text}],
        options={"temperature": 0.2, "num_ctx": 16384}
    )
    
    return response["message"]["content"].strip()


async def run_coder_agent(file_path: str, prompt: str, right_context: str, plan: str) -> str:
    """
    Coder Agent: Nhận kế hoạch từ Planner và code hiện tại để sinh ra đúng 1 dòng code hoàn thành.
    """
    prompt_text = f"""Bạn là một lập trình viên Python tối giản và chính xác.
Nhiệm vụ của bạn là hoàn thành dòng code còn thiếu ngay tiếp theo ký tự cuối cùng của `Prompt Code`, dựa trên kế hoạch thiết kế của Planner.

[TARGET FILE PATH]
{file_path}

[PROMPT CODE]
```python
{prompt}
```

[RIGHT CONTEXT]
```python
{right_context}
```

[PLANNER DESIGN PLAN]
{plan}

[LƯU Ý QUAN TRỌNG VỀ ĐỊNH DẠNG ĐẦU RA]
- Hãy sinh ra ĐÚNG dòng code hoàn chỉnh (bao gồm cả phần đầu dòng đã có sẵn ở dòng cuối cùng của `Prompt Code`).
- Ví dụ: nếu dòng cuối cùng của `Prompt Code` là `    old_tail = tokenizer.decode(generator.`, bạn cần xuất ra dòng hoàn chỉnh: `    old_tail = tokenizer.decode(generator.sequence_actual[:, -max_stop_string:])[0]`
- KHÔNG giải thích, KHÔNG viết markdown codeblock (không dùng ```), KHÔNG bình luận gì thêm.
"""

    response = await ollama_client.chat(
        model=config.MODEL_LLM,
        messages=[{"role": "user", "content": prompt_text}],
        options={"temperature": 0.0, "num_ctx": 16384}
    )
    
    code_out = response["message"]["content"].strip()
    
    if code_out.startswith("```python"):
        code_out = code_out[9:]
    elif code_out.startswith("```"):
        code_out = code_out[3:]
    if code_out.endswith("```"):
        code_out = code_out[:-3]
        
    return code_out.strip()


def extract_completion_suffix(prompt: str, coder_out: str) -> str:
    """
    Trích xuất phần đuôi hoàn thành bằng cách loại bỏ tiền tố đã có trong dòng cuối của prompt.
    """
    prompt_lines = prompt.splitlines()
    if not prompt_lines:
        return coder_out
    
    last_line = prompt_lines[-1]
    last_line_stripped = last_line.strip()
    coder_out_stripped = coder_out.strip()
    
    if last_line_stripped and coder_out_stripped.startswith(last_line_stripped):
        suffix = coder_out_stripped[len(last_line_stripped):]
        return suffix.strip()
        
    return coder_out_stripped


async def run_mas_completion(file_path: str, prompt: str, right_context: str, crossfile_list: list, groundtruth: str = "", top_k: int = 2) -> Tuple[str, str, str]:
    """
    Chạy toàn bộ MAS pipeline cho 1 ví dụ:
    1. Dựng codebase tạm.
    2. Chạy AST extractor và lưu vào graph / ChromaDB tạm thời.
    3. Lấy context thông qua GraphRAG.
    4. Chạy Planner để sinh Plan.
    5. Chạy Coder để sinh code hoàn chỉnh.
    6. Trích xuất phần đuôi hoàn thành.
    """
    temp_dir = tempfile.mkdtemp(prefix="rag_eval_")
    
    temp_chroma_dir = os.path.join(temp_dir, "chroma")
    temp_graph_path = os.path.join(temp_dir, "code_graph.gml")
    temp_collection_name = "temp_codebase"
    
    orig_source_dir = config.SOURCE_CODE_DIR
    orig_chroma_dir = config.CHROMA_DB_DIR
    orig_graph_path = config.GRAPH_FILE_PATH
    orig_collection_name = config.COLLECTION_NAME
    
    try:
        reconstruct_temp_codebase(file_path, prompt, right_context, crossfile_list, temp_dir, groundtruth)
        
        config.SOURCE_CODE_DIR = temp_dir
        config.CHROMA_DB_DIR = temp_chroma_dir
        config.GRAPH_FILE_PATH = temp_graph_path
        config.COLLECTION_NAME = temp_collection_name
        
        graph, chunks = parse_codebase_to_graph_and_chunks(config.SOURCE_CODE_DIR)
        await build_vector_and_graph_db(graph, chunks)
        
        query = prompt.splitlines()[-1] if prompt.splitlines() else prompt
        retrieved_context = await retrieve_context(
            query=query,
            db_dir=temp_chroma_dir,
            collection_name=temp_collection_name,
            graph_path=temp_graph_path,
            top_k=top_k
        )
        
        plan = await run_planner_agent(file_path, prompt, right_context, retrieved_context)
        
        coder_out = await run_coder_agent(file_path, prompt, right_context, plan)
        
        # Trích xuất phần completion đuôi
        completion = extract_completion_suffix(prompt, coder_out)
        
        return completion, plan, retrieved_context

    finally:
        config.SOURCE_CODE_DIR = orig_source_dir
        config.CHROMA_DB_DIR = orig_chroma_dir
        config.GRAPH_FILE_PATH = orig_graph_path
        config.COLLECTION_NAME = orig_collection_name
        
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
