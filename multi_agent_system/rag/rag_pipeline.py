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

    @staticmethod
    def get_codebase_manifest(graph: nx.DiGraph) -> str:
        """Create a compact manifest of every file and definition in the graph."""
        if not graph or graph.number_of_nodes() == 0:
            return "Codebase hiện tại trống (Không có tệp tin hoặc node nào)."

        file_nodes = sorted(
            (n for n, d in graph.nodes(data=True) if d.get("type") == "file"),
            key=lambda node_id: str(graph.nodes[node_id].get("path", node_id))
        )
        class_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") in ["class", "struct"]]
        # Đếm cả function độc lập lẫn method thuộc class/struct
        func_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") in ["function", "method"]]

        summary = [
            "### [CODEBASE MANIFEST TỪ ĐỒ THỊ]",
            f"Tệp: {len(file_nodes)} | Class/Struct: {len(class_nodes)} | Hàm/Method: {len(func_nodes)}",
        ]

        for fn in file_nodes:
            file_data = graph.nodes[fn]
            fpath = str(file_data.get("path", fn)).replace("\\", "/")
            summary.append(f"- [{str(file_data.get('lang', '')).upper()}] {fpath}")

            imports = sorted(
                str(graph.nodes[node_id].get("name", node_id))
                for _, node_id, edge_data in graph.out_edges(fn, data=True)
                if edge_data.get("relation") == "IMPORTS"
            )
            if imports:
                summary.append(f"  imports: {', '.join(imports)}")

            definitions = [
                node_id
                for _, node_id, edge_data in graph.out_edges(fn, data=True)
                if edge_data.get("relation") == "DEFINES"
            ]
            definitions.sort(
                key=lambda node_id: (
                    str(graph.nodes[node_id].get("type", "")),
                    str(graph.nodes[node_id].get("name", ""))
                )
            )
            for node_id in definitions:
                data = graph.nodes[node_id]
                node_type = data.get("type", "definition")
                name = data.get("name", node_id)
                if node_type in ["class", "struct"]:
                    bases = data.get("bases", "")
                    suffix = f" extends/implements {bases}" if bases else ""
                    summary.append(f"  {node_type} {name}{suffix}")
                else:
                    args = data.get("args", "()")
                    summary.append(f"  {node_type} {name}{args}")

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

        for nid in sorted(all_related_node_ids):
            if not graph.has_node(nid):
                continue

            ndata = graph.nodes[nid]
            if ndata.get("type") not in ["function", "method"]:
                continue

            code = str(ndata.get("code", "")).strip()
            if not code:
                continue

            lang = str(ndata.get("lang", ""))
            retrieved_chunks.append(
                f"File: {ndata.get('file', '')}\n"
                f"```{lang}\n{code}\n```"
            )

        manifest = self.get_codebase_manifest(graph)
        if not retrieved_chunks:
            return manifest

        retrieved_context = "\n\n---\n\n".join(retrieved_chunks)
        return f"{manifest}\n\n### [CÁC ĐOẠN LIÊN QUAN ĐƯỢC TRUY XUẤT]\n{retrieved_context}"