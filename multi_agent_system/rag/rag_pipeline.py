"""
multi_agent_system.rag.rag_pipeline
==================================
Pipeline truy vấn đồ thị tri thức (GraphRAG) phục vụ Agent Planner.
Hỗ trợ tìm kiếm Semantic Vector kết hợp mở rộng lân cận Đồ thị (Graph Neighbor Expansion).
"""

import networkx as nx
from typing import Set, List, Dict, Any, Optional
from .graph_store import GraphKnowledgeStore
from .. import config

class GraphRAGRetriever:
    def __init__(self, store: Optional[GraphKnowledgeStore] = None):
        self.store = store or GraphKnowledgeStore()

    @staticmethod
    def expand_nodes_via_graph(graph: nx.DiGraph, seed_node_ids: List[str]) -> Set[str]:
        """
        Mở rộng từ danh sách seed nodes để thu thập các node láng giềng 1-hop và 2-hop
        dựa trên các cạnh IMPORTS, DEFINES, CALLS.
        """
        expanded_nodes = set(seed_node_ids)
        for node_id in seed_node_ids:
            if not graph.has_node(node_id):
                continue
            # Lấy các node gọi tới hoặc được gọi từ node này
            predecessors = list(graph.predecessors(node_id))
            expanded_nodes.update(predecessors)
            successors = list(graph.successors(node_id))
            expanded_nodes.update(successors)
            
            # 2-hop expansion
            for succ in successors:
                if graph.has_node(succ):
                    expanded_nodes.update(list(graph.successors(succ)))

        return expanded_nodes

    def get_codebase_summary(self, graph: nx.DiGraph) -> str:
        """Tóm tắt cấu trúc cây thư mục và các thành phần chính trong đồ thị."""
        if not graph or graph.number_of_nodes() == 0:
            return "Codebase hiện tại trống (Không có tệp tin hoặc node nào)."

        file_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "file"]
        class_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") in ["class", "struct"]]
        # Đếm cả function độc lập lẫn method thuộc class/struct
        func_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") in ["function", "method"]]

        summary = [
            f"- Tổng số Tệp tin: {len(file_nodes)}",
            f"- Tổng số Class / Struct: {len(class_nodes)}",
            f"- Tổng số Hàm / Phương thức: {len(func_nodes)}",
            "\nDanh sách các tệp và định nghĩa:"
        ]

        for fn in file_nodes:
            fpath = graph.nodes[fn].get("path", fn)
            flang = graph.nodes[fn].get("lang", "")
            defines = [v for u, v, d in graph.out_edges(fn, data=True) if d.get("relation") == "DEFINES"]
            symbols = []
            for d in defines:
                ddata = graph.nodes.get(d, {})
                symbols.append(f"{ddata.get('type')}: {ddata.get('name')}")
            sym_str = f" -> [{', '.join(symbols)}]" if symbols else ""
            summary.append(f"  * [{flang.upper()}] {fpath}{sym_str}")

        return "\n".join(summary)

    async def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Truy vấn ngữ cảnh kết hợp Vector và Graph cho Planner Agent.
        """
        graph = self.store.graph
        if graph.number_of_nodes() == 0:
            graph = self.store.load_existing_graph()

        retrieved_chunks = []
        seed_node_ids: List[str] = []

        # 1. Truy vấn từ ChromaDB
        self.store._init_chroma()
        if self.store.collection and self.store.collection.count() > 0:
            try:
                embeddings = await self.store.get_embeddings([query])
                if embeddings:
                    results = self.store.collection.query(
                        query_embeddings=embeddings,
                        n_results=min(top_k, self.store.collection.count())
                    )
                    if results and results.get("ids") and len(results["ids"]) > 0:
                        seed_node_ids = results["ids"][0]
            except Exception as e:
                print(f"⚠️ [GraphRAGRetriever] Lỗi tìm kiếm ChromaDB: {e}")

        # 2. Nếu không có seed từ vector, tìm kiếm node theo từ khóa trong tên hàm/file
        if not seed_node_ids and graph.number_of_nodes() > 0:
            query_lower = query.lower()
            for nid, data in graph.nodes(data=True):
                name = str(data.get("name", "")).lower()
                path = str(data.get("path", "")).lower()
                if (name and name in query_lower) or (path and path in query_lower):
                    seed_node_ids.append(nid)
                    if len(seed_node_ids) >= top_k:
                        break

        # 3. Mở rộng đồ thị (Graph Expansion)
        all_related_node_ids = self.expand_nodes_via_graph(graph, seed_node_ids)

        for nid in all_related_node_ids:
            if self.store.collection and self.store.collection.count() > 0:
                try:
                    doc = self.store.collection.get(ids=[nid])
                    if doc and doc.get("documents") and len(doc["documents"]) > 0 and doc["documents"][0]:
                        retrieved_chunks.append(doc["documents"][0])
                        continue
                except Exception:
                    pass

            if graph.has_node(nid):
                ndata = graph.nodes[nid]
                ntype = ndata.get("type", "unknown")
                # Hỗ trợ đầy đủ cả method bên cạnh function, class, struct
                if ntype in ["function", "method", "class", "struct"]:
                    retrieved_chunks.append(
                        f"Graph Node: {nid}\nType: {ntype}\nName: {ndata.get('name')}\nFile: {ndata.get('file')}\nCode:\n{ndata.get('code', '')}"
                    )
                else:
                    retrieved_chunks.append(f"Graph Node: {nid} (Type: {ntype})")

        if not retrieved_chunks:
            return self.get_codebase_summary(graph)

        return "\n\n---\n\n".join(retrieved_chunks)