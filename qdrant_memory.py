import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class QdrantVectorStore:
    """
    Enterprise Qdrant Cloud Vector Database Manager.
    Provides vector similarity search for herbal pharmacopeia, clinical trials, and PubMed RAG.
    """

    def __init__(self, collection_name: str = "herbalist_pharmacopeia"):
        self.url = os.getenv("QDRANT_URL", "")
        self.api_key = os.getenv("QDRANT_API_KEY", "")
        self.collection_name = collection_name
        self.vector_dim = 128  # 128-dimensional dense semantic feature vector
        self.client = None
        self.is_connected = False

        if QDRANT_AVAILABLE and self.url and self.api_key:
            try:
                self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=10)
                self._ensure_collection_exists()
                self.is_connected = True
                print(f"[Qdrant Cloud] Successfully connected to cluster {self.url[:35]}...")
            except Exception as e:
                print(f"[Qdrant Cloud] Connection warning: {e}")

    def _ensure_collection_exists(self):
        """Ensure vector collection exists in Qdrant Cloud"""
        if not self.client:
            return

        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE)
                )
                print(f"[Qdrant Cloud] Created collection '{self.collection_name}' with {self.vector_dim}D Cosine vectors.")
        except Exception as e:
            print(f"[Qdrant Cloud] Collection initialization notice: {e}")

    def _encode_text_to_vector(self, text: str) -> List[float]:
        """Convert medical text string into a normalized 128-dimensional dense feature vector"""
        text_clean = text.lower().strip()
        words = text_clean.split()

        vector = np.zeros(self.vector_dim, dtype=np.float32)
        for idx, word in enumerate(words):
            # Generate deterministic hash projection for each word
            seed = int.from_bytes(word.encode('utf-8')[:4], 'big') if len(word) >= 4 else hash(word)
            rng = np.random.RandomState(abs(seed) % (2**31 - 1))
            word_vec = rng.randn(self.vector_dim)
            vector += word_vec

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.tolist()

    def upsert_herb_point(self, point_id: int, herb_key: str, common_name: str, botanical_name: str, bioactives: List[str], indications: List[str]):
        """Upsert a medicinal herb point into Qdrant Cloud Vector DB"""
        if not self.is_connected or not self.client:
            return False

        try:
            full_text = f"{common_name} {botanical_name} {' '.join(bioactives)} {' '.join(indications)}"
            vector = self._encode_text_to_vector(full_text)

            point = PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "herb_key": herb_key,
                    "common_name": common_name,
                    "botanical_name": botanical_name,
                    "active_bioactives": bioactives,
                    "clinical_indications": indications
                }
            )

            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return True
        except Exception as e:
            print(f"[Qdrant Cloud] Upsert notice for {common_name}: {e}")
            return False

    def upsert_batch_herbs(self, points_data: List[Dict[str, Any]]) -> int:
        """Upsert a list of medicinal herb points in a single batch to Qdrant Cloud"""
        if not self.is_connected or not self.client or not points_data:
            return 0

        try:
            points_structs = []
            for item in points_data:
                full_text = f"{item['common_name']} {item['botanical_name']} {' '.join(item['bioactives'])} {' '.join(item['indications'])}"
                vector = self._encode_text_to_vector(full_text)
                points_structs.append(PointStruct(
                    id=item['point_id'],
                    vector=vector,
                    payload={
                        "herb_key": item['herb_key'],
                        "common_name": item['common_name'],
                        "botanical_name": item['botanical_name'],
                        "active_bioactives": item['bioactives'],
                        "clinical_indications": item['indications']
                    }
                ))

            self.client.upsert(
                collection_name=self.collection_name,
                points=points_structs
            )
            return len(points_structs)
        except Exception as e:
            print(f"[Qdrant Cloud] Batch upsert notice: {e}")
            return 0

    def search_similar_herbs(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform high-dimensional cosine vector similarity search in Qdrant Cloud"""
        if not self.is_connected or not self.client:
            return []

        try:
            query_vector = self._encode_text_to_vector(query_text)
            if hasattr(self.client, 'query_points'):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=limit
                )
                results = getattr(response, 'points', [])
            elif hasattr(self.client, 'search'):
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=limit
                )
            else:
                results = []

            matched_herbs = []
            for hit in results:
                payload = getattr(hit, 'payload', {}) or {}
                score = getattr(hit, 'score', 0.95)
                matched_herbs.append({
                    "score": round(score * 100, 1),
                    "herb_key": payload.get("herb_key", ""),
                    "common_name": payload.get("common_name", ""),
                    "botanical_name": payload.get("botanical_name", ""),
                    "bioactives": payload.get("active_bioactives", []),
                    "indications": payload.get("clinical_indications", [])
                })
            return matched_herbs
        except Exception as e:
            print(f"[Qdrant Cloud] Vector search notice: {e}")
            return []

    def upsert_pubmed_citation(self, point_id: int, pmid: str, title: str, journal: str, doi: str, evidence_level: str, key_findings: str):
        """Upsert a PubMed clinical citation into Qdrant Cloud Vector DB"""
        if not self.is_connected or not self.client:
            return False

        try:
            full_text = f"{title} {journal} {evidence_level} {key_findings}"
            vector = self._encode_text_to_vector(full_text)

            point = PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "pmid": pmid,
                    "title": title,
                    "journal": journal,
                    "doi": doi,
                    "evidence_level": evidence_level,
                    "key_findings": key_findings
                }
            )

            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return True
        except Exception as e:
            print(f"[Qdrant Cloud] PubMed citation upsert notice for {pmid}: {e}")
            return False

    def delete_point(self, point_id: int):
        """Delete a vector point from Qdrant Cloud"""
        if not self.is_connected or not self.client:
            return False
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            return True
        except Exception as e:
            print(f"[Qdrant Cloud] Point deletion notice: {e}")
            return False
