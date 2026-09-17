import networkx as nx
import chromadb
from typing import Set, List
import config
from storage.db_manager import get_embeddings, ollama_client

def expand_nodes_via_graph(graph: nx.DiGraph, seed_node_ids: List[str]) -> Set[str]:
    """Mở rộng từ Seed Nodes thu thập các 1-Hop & 2-Hop Neighbor Nodes trong Đồ thị."""
    expanded_nodes = set(seed_node_ids)
    for node_id in seed_node_ids:
        if not graph.has_node(node_id):
            continue
        predecessors = list(graph.predecessors(node_id))
        expanded_nodes.update(predecessors)
        
        successors = list(graph.successors(node_id))
        expanded_nodes.update(successors)
        
    return expanded_nodes

async def ask_graphrag_codebase(query: str, top_k: int = 2) -> str:
    chroma_client = chromadb.PersistentClient(path=config.CHROMA_DB_DIR)
    collection = chroma_client.get_collection(name=config.COLLECTION_NAME)
    graph = nx.read_gml(config.GRAPH_FILE_PATH)

    query_embedding = (await get_embeddings([query]))[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    seed_node_ids = results["ids"][0]
    
    all_related_node_ids = expand_nodes_via_graph(graph, seed_node_ids)

    retrieved_chunks = []
    for nid in all_related_node_ids:
        doc = collection.get(ids=[nid])
        if doc and doc["documents"]:
            retrieved_chunks.append(doc["documents"][0])
        elif graph.has_node(nid):
            ndata = graph.nodes[nid]
            retrieved_chunks.append(f"Graph Connection Node: {nid} (Type: {ndata.get('type', 'ref')})")

    context_str = "\n\n---\n\n".join(retrieved_chunks)
    
    prompt = f"""Bạn là một chuyên gia phân tích codebase Python. Sử dụng Đồ thị tri thức (Graph Knowledge) được trích xuất dưới đây để trả lời câu hỏi.

[GRAPH RETRIEVED CONTEXT (VECTOR + KNOWLEDGE GRAPH)]
{context_str}

[CÂU HỎI NGƯỜI DÙNG]
{query}

[YÊU CẦU TRẢ LỜI]
- Giải thích rõ luồng thực thi, mối quan hệ giữa các Class/Function (ai gọi ai, class nào chứa hàm nào).
- Chỉ rõ chính xác tên File, Class, hoặc Function liên quan.
"""

    response = await ollama_client.chat(
        model=config.MODEL_LLM,
        messages=[{"role": "user", "content": prompt}],
        options={"num_ctx": 16384}
    )
    
    return response["message"]["content"]