import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load a pre-trained sentence transformer model
# all-MiniLM-L6-v2 is fast and provides good embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

class VectorStore:
    def __init__(self, dimension=384):
        self.dimension = dimension
        # Using L2 distance
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_map = {}
        self.current_id = 0

    def add_texts(self, texts, metadata=None):
        if not texts:
            return []
            
        embeddings = model.encode(texts)
        embeddings = np.array(embeddings).astype('float32')
        
        self.index.add(embeddings)
        
        ids = []
        for i, text in enumerate(texts):
            self.id_map[self.current_id] = {
                "text": text,
                "metadata": metadata[i] if metadata else {}
            }
            ids.append(self.current_id)
            self.current_id += 1
            
        return ids

    def search(self, query, top_k=5):
        if self.index.ntotal == 0:
            return []
            
        query_vector = model.encode([query])
        query_vector = np.array(query_vector).astype('float32')
        
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1: # valid index
                results.append({
                    "id": idx,
                    "distance": distances[0][i],
                    "data": self.id_map.get(idx)
                })
        return results

def compute_similarity(text1, text2):
    """Computes pure Cosine Similarity (0-1) between two strings using SentenceTransformers."""
    if not text1 or not text2:
        return 0.0
    
    # Memory optimization: truncate long inputs
    t1 = text1[:5000] if len(text1) > 5000 else text1
    t2 = text2[:5000] if len(text2) > 5000 else text2
        
    embedding1 = model.encode(t1)
    embedding2 = model.encode(t2)
    
    # Utilizing semantic util for faster cosine math
    cosine_sim = util.cos_sim(embedding1, embedding2).item()
    return float(np.clip(cosine_sim, 0.0, 1.0))

# Initialize a global instance for the app to use
store = VectorStore()
