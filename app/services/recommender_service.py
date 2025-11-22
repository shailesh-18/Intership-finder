# import numpy as np
# import faiss
# from typing import List, Dict
# from flask import current_app

# from ..models.db import db
# from ..models.internship import Internship
# from .embedding_service import EmbeddingService


# class RecommenderService:
#     def __init__(self, embedding_service: EmbeddingService):
#         self.embedding_service = embedding_service
#         self.index = None
#         self.id_map: list[int] = []  # index -> internship.id

#     def rebuild_index(self) -> None:
#         """Rebuild FAISS index from all internships in DB."""
#         internships: list[Internship] = Internship.query.filter(
#             Internship.embedding_json.isnot(None)
#         ).all()

#         if not internships:
#             self.index = None
#             self.id_map = []
#             current_app.logger.info("No internships with embeddings yet.")
#             return

#         vectors = []
#         self.id_map = []

#         for intr in internships:
#             emb = self.embedding_service.embedding_from_json(intr.embedding_json)
#             if emb is not None:
#                 vectors.append(emb)
#                 self.id_map.append(intr.id)

#         if not vectors:
#             self.index = None
#             self.id_map = []
#             return

#         mat = np.vstack(vectors).astype("float32")
#         dim = mat.shape[1]

#         self.index = faiss.IndexFlatIP(dim)  # cosine similarity (with normalized vectors)
#         self.index.add(mat)
#         current_app.logger.info(f"FAISS index built with {len(self.id_map)} vectors.")

#     def add_internship_to_index(self, internship: Internship) -> None:
#         """Add a single internship to FAISS index (used after scraping)."""
#         emb = self.embedding_service.embedding_from_json(internship.embedding_json)
#         if emb is None:
#             return

#         emb = emb.reshape(1, -1).astype("float32")

#         if self.index is None:
#             dim = emb.shape[1]
#             self.index = faiss.IndexFlatIP(dim)
#             self.id_map = []

#         self.index.add(emb)
#         self.id_map.append(internship.id)

#     def recommend(self, profile_text: str, top_k: int = 10) -> List[Dict]:
#         """Return top-k recommended internships based on profile text."""
#         if self.index is None or not self.id_map:
#             return []

#         query_vec = self.embedding_service.encode_text(profile_text)
#         query_vec = query_vec.reshape(1, -1).astype("float32")

#         scores, indices = self.index.search(query_vec, top_k)
#         scores = scores[0]
#         indices = indices[0]

#         results: List[Dict] = []

#         for score, idx in zip(scores, indices):
#             if idx == -1:
#                 continue
#             internship_id = self.id_map[idx]
#             intr = Internship.query.get(internship_id)
#             if intr is None:
#                 continue

#             data = intr.to_dict()
#             data["score"] = float(score)
#             results.append(data)

#         # sort by score desc (FAISS already does this, but just in case)
#         results.sort(key=lambda x: x["score"], reverse=True)
#         return results
import numpy as np
import faiss
from typing import List, Dict, Optional
from flask import current_app

from ..models.db import db
from ..models.internship import Internship
from .embedding_service import EmbeddingService


class RecommenderService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.index: Optional[faiss.IndexFlatIP] = None
        self.id_map: list[int] = []  # index -> internship.id

    def rebuild_index(self) -> None:
        """Rebuild FAISS index from all internships in DB."""
        internships: list[Internship] = Internship.query.filter(
            Internship.embedding_json.isnot(None)
        ).all()

        if not internships:
            self.index = None
            self.id_map = []
            current_app.logger.info("No internships with embeddings yet.")
            return

        vectors = []
        self.id_map = []

        for intr in internships:
            emb = self.embedding_service.embedding_from_json(intr.embedding_json)
            if emb is not None:
                vectors.append(emb)
                self.id_map.append(intr.id)

        if not vectors:
            self.index = None
            self.id_map = []
            return

        mat = np.vstack(vectors).astype("float32")
        dim = mat.shape[1]

        self.index = faiss.IndexFlatIP(dim)  # cosine similarity (with normalized vectors)
        self.index.add(mat)
        current_app.logger.info(f"FAISS index built with {len(self.id_map)} vectors.")

    def add_internship_to_index(self, internship: Internship) -> None:
        """Add a single internship to FAISS index (used after scraping)."""
        emb = self.embedding_service.embedding_from_json(internship.embedding_json)
        if emb is None:
            return

        emb = emb.reshape(1, -1).astype("float32")

        if self.index is None:
            dim = emb.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.id_map = []

        self.index.add(emb)
        self.id_map.append(internship.id)

    # ------------- NEW: hybrid scoring helper methods -------------

    @staticmethod
    def _normalize_text(s: str) -> str:
        return (s or "").strip().lower()

    @staticmethod
    def _tokenize(s: str) -> list[str]:
        return [t for t in RecommenderService._normalize_text(s).replace(",", " ").split() if t]

    @staticmethod
    def _parse_skills(skills_field) -> list[str]:
        if isinstance(skills_field, list):
            return [RecommenderService._normalize_text(s) for s in skills_field if s]
        if isinstance(skills_field, str):
            return [RecommenderService._normalize_text(s) for s in skills_field.split(",") if s.strip()]
        return []

    def _compute_hybrid_score(
        self,
        internship: Dict,
        faiss_score: float,
        user_skills: list[str],
        location_pref: str,
        interests: str,
    ) -> float:
        """
        Combine FAISS similarity with:
        - skill overlap
        - location match
        - interest keyword match
        """
        title = self._normalize_text(internship.get("title", ""))
        desc = self._normalize_text(internship.get("description", ""))
        location = self._normalize_text(internship.get("location", ""))
        stipend = self._normalize_text(internship.get("stipend", ""))

        intr_skills = self._parse_skills(internship.get("skills", []))

        # skill overlap: Jaccard with user skills
        user_skills_norm = [self._normalize_text(s) for s in user_skills or []]
        set_user = set(user_skills_norm)
        set_intr = set(intr_skills)
        if set_user and set_intr:
            overlap = len(set_user & set_intr) / len(set_user)
        else:
            overlap = 0.0

        # location match
        loc_match = 0.0
        loc_pref_norm = self._normalize_text(location_pref)
        if loc_pref_norm:
            if loc_pref_norm in location:
                loc_match = 1.0
            elif any(tok in location for tok in loc_pref_norm.split()):
                loc_match = 0.5

        # interests keywords in title/description
        interest_norm = self._normalize_text(interests)
        interest_tokens = [t for t in interest_norm.replace(",", " ").split() if len(t) > 3]
        interest_match = 0.0
        if interest_tokens:
            hits = sum(1 for t in interest_tokens if t in title or t in desc)
            if hits:
                interest_match = min(1.0, hits / len(interest_tokens))

        # weights (you can tune these)
        w_faiss = 0.6
        w_skills = 0.2
        w_location = 0.1
        w_interest = 0.1

        final_score = (
            w_faiss * float(faiss_score)
            + w_skills * overlap
            + w_location * loc_match
            + w_interest * interest_match
        )
        return final_score

    # ------------- MAIN recommend -------------

    def recommend(
        self,
        profile_text: str,
        skills: Optional[list[str]] = None,
        location_pref: str = "",
        interests: str = "",
        top_k: int = 10,
    ) -> List[Dict]:
        """Return top-k recommended internships based on profile text + extra info."""
        if self.index is None or not self.id_map:
            return []

        skills = skills or []

        # 1) Vector search
        query_vec = self.embedding_service.encode_text(profile_text)
        query_vec = query_vec.reshape(1, -1).astype("float32")

        k_candidates = max(top_k * 3, top_k)  # get more, re-rank, then cut
        scores, indices = self.index.search(query_vec, k_candidates)
        scores = scores[0]
        indices = indices[0]

        raw_results: List[Dict] = []

        for score, idx in zip(scores, indices):
            if idx == -1:
                continue
            internship_id = self.id_map[idx]
            intr = Internship.query.get(internship_id)
            if intr is None:
                continue

            data = intr.to_dict()
            data["faiss_score"] = float(score)
            raw_results.append(data)

        # 2) Hybrid re-scoring
        reranked: List[Dict] = []
        for item in raw_results:
            hybrid_score = self._compute_hybrid_score(
                internship=item,
                faiss_score=item["faiss_score"],
                user_skills=skills,
                location_pref=location_pref,
                interests=interests,
            )
            item["score"] = float(hybrid_score)
            reranked.append(item)

        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:top_k]

    def rank_from_raw(
        self,
        profile_text: str,
        skills: list[str],
        location_pref: str,
        interests: str,
        candidates: list[Dict],
        top_k: int = 10,
    ) -> list[Dict]:
        """
        Live-search ke liye:
        - candidates = raw scraped items (not in DB)
        - embeddings yahi pe compute honge
        - FAISS ke bina direct cosine similarity + hybrid score
        """
        if not candidates:
            return []

        # Query embedding
        query_vec = self.embedding_service.encode_text(profile_text).astype("float32")

        ranked: list[Dict] = []

        for item in candidates:
            title = item.get("title", "")
            company = item.get("company", "")
            location = item.get("location", "")
            duration = item.get("duration", "")
            stipend = item.get("stipend", "")
            description = item.get("description", "")
            skills_list = item.get("skills", []) or []

            text_for_emb = (
                f"Internship Title: {title}. "
                f"Company: {company}. "
                f"Skills required: {', '.join(skills_list)}. "
                f"Location: {location}. "
                f"Type: {duration}. "
                f"Stipend offered: {stipend}. "
                f"Responsibilities: {description}. "
                f"This internship requires: {', '.join(skills_list)}."
            )

            intr_vec = self.embedding_service.encode_text(text_for_emb).astype("float32")
            faiss_score = float(np.dot(query_vec, intr_vec))  # cosine, embeddings normalized

            # Hybrid score reuse
            hybrid_score = self._compute_hybrid_score(
                internship=item,
                faiss_score=faiss_score,
                user_skills=skills,
                location_pref=location_pref,
                interests=interests,
            )

            out = item.copy()
            out["faiss_score"] = faiss_score
            out["score"] = float(hybrid_score)
            ranked.append(out)

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:top_k]
