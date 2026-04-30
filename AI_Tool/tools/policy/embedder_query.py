
"""
使用向量检索来找到完整的正文
"""

import os
import sys
from .embedder import Embedder
from .init_all_txt import extract_pdf_by_font_group

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
ALL_TXT_PATH = os.path.abspath(os.path.join(BASE_DIR, "files/学生手册", "all.txt"))
PDF_PATH = os.path.abspath(os.path.join(BASE_DIR, "files/学生手册", "2025年本科学生手册.pdf"))
CUT_MARK = "#"
CUT_MARK_NUM = 20
SEPARATOR = CUT_MARK * CUT_MARK_NUM
CHUNK_SIZE = 200
RETURN_NUM = 5


class EmbedderQuery:
    def __init__(self):
        self.text_embedder = Embedder()
        self.large_blocks = []
        self.small_chunks = []
        self.chunk_embeddings = None
    
        
    def ensure_all_txt(self):
        if not os.path.exists(ALL_TXT_PATH):
            print("all.txt 不存在，开始初始化...")
            extract_pdf_by_font_group(PDF_PATH, ALL_TXT_PATH)
    
    def load_and_chunk(self):
        self.ensure_all_txt()
        
        with open(ALL_TXT_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        self.large_blocks = []
        blocks = content.split(SEPARATOR)[2:]
        #blocks = [b.strip() for b in blocks if b.strip()]
        
        for block in blocks:
            self.large_blocks.append({
                "content": block,
                "length": len(block)
            })
        
        self.small_chunks = []
        for large_idx, large_block in enumerate(self.large_blocks):
            content = large_block["content"]
            content_len = large_block["length"]
            
            # 直接循环
            for i in range(0, content_len, CHUNK_SIZE):
                chunk = content[i:i + CHUNK_SIZE]
                self.small_chunks.append({
                    "content": chunk,
                    "large_block_idx": large_idx
                })
    
    def build_index(self):
        if not self.small_chunks:
            self.load_and_chunk()
        
        print("[EmbedderQuery] 正在构建向量索引...")
        chunk_texts = [chunk["content"] for chunk in self.small_chunks]
        self.chunk_embeddings = self.text_embedder.encode(chunk_texts)
        print(f"[EmbedderQuery] 向量索引构建完成，共 {len(self.small_chunks)} 个文本块")
    
    def search(self, query,top_k=RETURN_NUM):
        """
        搜索并返回结果
        """
        if self.chunk_embeddings is None:
            self.build_index()
        
        query_embedding = self.text_embedder.encode(query)[0]
        similarities = []
        
        for i, chunk_embedding in enumerate(self.chunk_embeddings):
            sim = self.text_embedder.similarity(query_embedding, chunk_embedding)
            similarities.append({
                "chunk": self.small_chunks[i],
                "similarity": sim
            })
        
        # 简单排序
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_chunks = similarities[:top_k]
        
        small_chunks_content = []
        for top_chunk in top_chunks:
            small_chunks_content.append(top_chunk["chunk"]["content"])
        
        used_large_indices = set()
        full_blocks_content = []
        
        for top_chunk in top_chunks:
            large_idx = top_chunk["chunk"]["large_block_idx"]
            if large_idx not in used_large_indices:
                used_large_indices.add(large_idx)
                full_blocks_content.append(self.large_blocks[large_idx]["content"])
        
        return {
            "small_chunks": small_chunks_content,
            "full_blocks": full_blocks_content
        }
