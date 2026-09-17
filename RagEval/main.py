import asyncio
import config
from extractors.ast_extractor import parse_codebase_to_graph_and_chunks
from storage.db_manager import build_vector_and_graph_db
from pipeline.rag_pipeline import ask_graphrag_codebase

async def main():
    graph, chunks = parse_codebase_to_graph_and_chunks(config.SOURCE_CODE_DIR)
    print(f"📦 Tạo thành công {len(chunks)} Graph Nodes từ codebase.")

    await build_vector_and_graph_db(graph, chunks)

    print("🤖 Hệ thống GraphRAG Codebase (AST + NetworkX + ChromaDB) đã sẵn sàng!\n")
    while True:
        try:
            user_query = input("\n👤 Bạn hỏi: ")
            if user_query.strip().lower() in ["exit", "quit", "q"]:
                break
            if not user_query.strip():
                continue

            print("🔍 Đang duyệt Đồ thị tri thức (Knowledge Graph) và phân tích...")
            answer = await ask_graphrag_codebase(user_query, top_k=2)
            print("\n--- CÂU TRẢ LỜI GRAPHRAG ---")
            print(answer)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    asyncio.run(main())