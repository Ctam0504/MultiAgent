import networkx as nx
import chromadb
from ollama import AsyncClient
from typing import List
import config
from models.code_models import CodeChunk

ollama_client = AsyncClient(host=config.OLLAMA_HOST, timeout=300.0)

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    response = await ollama_client.embed(model=config.MODEL_EMBED, input=texts)
    return response["embeddings"]

async def build_vector_and_graph_db(graph: nx.DiGraph, chunks: List[CodeChunk]):
    print(f"\n⚡ Bắt đầu nhúng {len(chunks)} Graph Nodes vào ChromaDB...")
    
    nx.write_gml(graph, config.GRAPH_FILE_PATH)
    print(f"✅ Đã lưu Đồ thị Codebase ({graph.number_of_nodes()} Nodes, {graph.number_of_edges()} Edges) tại '{config.GRAPH_FILE_PATH}'")

    chroma_client = chromadb.PersistentClient(path=config.CHROMA_DB_DIR)
    try:
        chroma_client.delete_collection(name=config.COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    contents = [c.content for c in chunks]
    ids = [c.id for c in chunks]
    metadatas = [c.to_metadata() for c in chunks]

    if contents:
        embeddings = await get_embeddings(contents)
        collection.add(documents=contents, embeddings=embeddings, metadatas=metadatas, ids=ids)
        print(f"✅ Đã lưu {collection.count()} vectors thành công vào ChromaDB!\n")
    else:
        print("⚠️ Không có chunks nào để nhúng vào ChromaDB!\n")