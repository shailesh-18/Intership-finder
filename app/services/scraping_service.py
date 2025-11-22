# # from typing import List, Dict
# # from flask import current_app

# # from ..models.db import db
# # from ..models.internship import Internship
# # from .embedding_service import EmbeddingService
# # from .recommender_service import RecommenderService
# # from ..scrapers.internshala import InternshalaScraper
# # from ..scrapers.internshala import InternshalaScraper
# # from ..scrapers.unstop import UnstopScraper
# # # plus any other scrapers you had


# # class ScrapingService:
# #     def __init__(
# #         self,
# #         embedding_service: EmbeddingService,
# #         recommender_service: RecommenderService,
# #     ):
# #         self.embedding_service = embedding_service
# #         self.recommender_service = recommender_service
# #         self.scrapers = [
# #             InternshalaScraper(),
# #             # Add more scrapers here later
# #         ]

# #     def run_all(self, pages_per_source: int = 1) -> int:
# #         """Run all scrapers, store results, build embeddings, update FAISS.

# #         Returns total new internships stored.
# #         """
# #         total_new = 0

# #         for scraper in self.scrapers:
# #             current_app.logger.info(f"Running scraper: {scraper.__class__.__name__}")
# #             data: List[Dict] = scraper.scrape(max_pages=pages_per_source)
# #             for item in data:
# #                 if not item.get("link"):
# #                     continue

# #                 existing = Internship.query.filter_by(link=item["link"]).first()
# #                 if existing:
# #                     continue

# #                 # Build a text blob for embedding
# #                 # profile_text = (
# #                 #     f"{item.get('title','')} at {item.get('company','')}. "
# #                 #     f"Location: {item.get('location','')}. "
# #                 #     f"Duration: {item.get('duration','')}. "
# #                 #     f"Skills: {', '.join(item.get('skills', []))}. "
# #                 #     f"Description: {item.get('description','')}"
# #                 # )
# #                 profile_text = (
# #     f"{item.get('title','')} at {item.get('company','')}. "
# #     f"Location: {item.get('location','')}. "
# #     f"Duration: {item.get('duration','')}. "
# #     f"Stipend: {item.get('stipend','')}. "
# #     f"Skills: {', '.join(item.get('skills', []))}. "
# #     f"Description: {item.get('description','')}"
# # )

# #                 emb = self.embedding_service.encode_text(profile_text)

# #                 # intr = Internship(
# #                 #     title=item.get("title", "N/A"),
# #                 #     company=item.get("company", "N/A"),
# #                 #     location=item.get("location", ""),
# #                 #     duration=item.get("duration", ""),
# #                 #     skills=",".join(item.get("skills", [])),
# #                 #     description=item.get("description", ""),
# #                 #     link=item["link"],
# #                 #     embedding_json=self.embedding_service.embedding_to_json(emb),
# #                 # )
# #                 intr = Internship(
# #     title=item.get("title", "N/A"),
# #     company=item.get("company", "N/A"),
# #     location=item.get("location", ""),
# #     duration=item.get("duration", ""),
# #     stipend=item.get("stipend", ""),    # ← NEW FIELD
# #     skills=",".join(item.get("skills", [])),
# #     description=item.get("description", ""),
# #     link=item["link"],
# #     embedding_json=self.embedding_service.embedding_to_json(emb),
# # )

# #                 db.session.add(intr)
# #                 db.session.flush()  # to get intr.id

# #                 # Add to FAISS index in memory
# #                 self.recommender_service.add_internship_to_index(intr)

# #                 total_new += 1

# #             db.session.commit()

# #         current_app.logger.info(f"Scraping finished. New internships: {total_new}")
# #         return total_new
# # class ScrapingService:
# #     def __init__(
# #         self,
# #         embedding_service: EmbeddingService,
# #         recommender_service: RecommenderService,
# #     ):
# #         self.embedding_service = embedding_service
# #         self.recommender_service = recommender_service
# #         self.scrapers = [
# #             InternshalaScraper(),
# #             UnstopScraper(),   # 👈 new source added
# #             # ExampleBoardScraper(),
# #             # ExampleAPIScraper(),
# #         ]
# # app/services/scraping_service.py

# from typing import List, Dict
# from flask import current_app

# from ..models.db import db
# from ..models.internship import Internship
# from .embedding_service import EmbeddingService
# from .recommender_service import RecommenderService
# from ..scrapers.internshala import InternshalaScraper
# from ..scrapers.unstop import UnstopScraper  # comment this line if you didn't add it yet


# class ScrapingService:
#     def __init__(
#         self,
#         embedding_service: EmbeddingService,
#         recommender_service: RecommenderService,
#     ):
#         self.embedding_service = embedding_service
#         self.recommender_service = recommender_service

#         # Register all sources here
#         self.scrapers = [
#             InternshalaScraper(),
#             UnstopScraper(),  # comment/remove if not ready
#         ]
    
#     def run_all(self, pages_per_source: int = 1) -> int:
#         """Run all scrapers, store results, build embeddings, update FAISS.

#         Returns:
#             int: total new internships stored.
#         """
#         total_new = 0

#         for scraper in self.scrapers:
#             current_app.logger.info(f"Running scraper: {scraper.__class__.__name__}")
#             data: List[Dict] = scraper.scrape(max_pages=pages_per_source)

#             for item in data:
#                 # Basic validation
#                 link = item.get("link")
#                 if not link:
#                     continue

#                 # Skip duplicates by link
#                 existing = Internship.query.filter_by(link=link).first()
#                 if existing:
#                     continue

#                 title = item.get("title", "N/A")
#                 company = item.get("company", "N/A")
#                 location = item.get("location", "")
#                 duration = item.get("duration", "")
#                 stipend = item.get("stipend", "")
#                 description = item.get("description", "")
#                 skills_list = item.get("skills", []) or []
#                 skills_str = ",".join(skills_list)

#                 # Build text for embedding
#                 # profile_text = (
#                 #     f"{title} at {company}. "
#                 #     f"Location: {location}. "
#                 #     f"Duration: {duration}. "
#                 #     f"Stipend: {stipend}. "
#                 #     f"Skills: {', '.join(skills_list)}. "
#                 #     f"Description: {description}"
#                 # )
#                 profile_text = (
#     f"Internship Title: {item.get('title','')}. "
#     f"Company: {item.get('company','')}. "
#     f"Skills required: {', '.join(skills_list)}. "
#     f"Location: {location}. "
#     f"Type: {duration}. "
#     f"Stipend offered: {stipend}. "
#     f"Responsibilities: {description}. "
#     f"This internship requires: {', '.join(skills_list)}."
# )


#                 emb = self.embedding_service.encode_text(profile_text)

#                 intr = Internship(
#                     title=title,
#                     company=company,
#                     location=location,
#                     duration=duration,
#                     stipend=stipend,
#                     skills=skills_str,
#                     description=description,
#                     link=link,
#                     embedding_json=self.embedding_service.embedding_to_json(emb),
#                 )

#                 db.session.add(intr)
#                 db.session.flush()  # assign intr.id
#                 self.recommender_service.add_internship_to_index(intr)

#                 total_new += 1

#             db.session.commit()

#         current_app.logger.info(f"Scraping finished. New internships: {total_new}")
#         return total_new

#     def live_search(
#         self,
#         profile_text: str,
#         skills: list[str],
#         location_pref: str,
#         interests: str,
#         pages_per_source: int = 1,
#         top_k: int = 10,
#     ) -> list[Dict]:
#         """
#         Live search:
#         - Har scraper se limited pages scrape karta hai (DB me nahi daalta)
#         - Saare candidates ko RecommenderService.rank_from_raw se score karta hai
#         - Sirf top_k results return karta hai
#         """
#         all_candidates: list[Dict] = []

#         for scraper in self.scrapers:
#             current_app.logger.info(
#                 f"[LIVE SEARCH] Running scraper: {scraper.__class__.__name__} "
#                 f"for {pages_per_source} pages"
#             )
#             data = scraper.scrape(max_pages=pages_per_source)
#             all_candidates.extend(data)

#         current_app.logger.info(
#             f"[LIVE SEARCH] Total candidates scraped: {len(all_candidates)}"
#         )

#         if not all_candidates:
#             return []

#         results = self.recommender_service.rank_from_raw(
#             profile_text=profile_text,
#             skills=skills,
#             location_pref=location_pref,
#             interests=interests,
#             candidates=all_candidates,
#             top_k=top_k,
#         )
#         return results
    
#         def _expand_skill_keywords(self, skills: list[str]) -> list[str]:
#         """
#         User skills ko normalize + expand karta hai (synonyms).
#         e.g. 'MERN' -> ['mern', 'react', 'node', 'express', 'mongodb']
#              'cyber security' -> related keywords
#         """
#         base = set()

#         for s in skills or []:
#             s_norm = (s or "").strip().lower()
#             if not s_norm:
#                 continue
#             base.add(s_norm)

#             # simple expansions
#             if "mern" in s_norm:
#                 base.update(["mern", "react", "node", "node.js", "express", "mongodb"])
#             if "full stack" in s_norm:
#                 base.update(["full stack", "frontend", "backend"])
#             if "cyber security" in s_norm or "cybersecurity" in s_norm:
#                 base.update(
#                     [
#                         "cyber security",
#                         "cybersecurity",
#                         "network security",
#                         "information security",
#                         "ethical hacking",
#                         "penetration testing",
#                         "security",
#                     ]
#                 )

#         return list(base)

#     def _filter_candidates_by_constraints(
#         self,
#         candidates: list[Dict],
#         skills: list[str],
#         location_pref: str,
#     ) -> list[Dict]:
#         """
#         Hard filter:
#         - Agar skills diye gaye hai -> kam se kam 1 skill keyword
#           title/description/skills me hona hi chahiye
#         - Agar location_pref diya hai -> location string me include hona chahiye
#         """
#         if not candidates:
#             return []

#         expanded_skills = self._expand_skill_keywords(skills)
#         loc_pref = (location_pref or "").strip().lower()

#         filtered: list[Dict] = []

#         for item in candidates:
#             title = (item.get("title") or "").lower()
#             desc = (item.get("description") or "").lower()
#             loc = (item.get("location") or "").lower()
#             skills_list = item.get("skills", []) or []
#             skills_text = " ".join(str(s) for s in skills_list).lower()

#             # --- skill condition ---
#             skill_ok = True
#             if expanded_skills:
#                 skill_ok = any(
#                     key in title or key in desc or key in skills_text
#                     for key in expanded_skills
#                 )

#             # --- location condition ---
#             loc_ok = True
#             if loc_pref:
#                 # simple contains check; can be improved with city synonyms
#                 loc_ok = loc_pref in loc

#             if skill_ok and loc_ok:
#                 filtered.append(item)

#         return filtered

# app/services/scraping_service.py

from typing import List, Dict
from flask import current_app

from ..models.db import db
from ..models.internship import Internship
from .embedding_service import EmbeddingService
from .recommender_service import RecommenderService
from ..scrapers.internshala import InternshalaScraper
from ..scrapers.unstop import UnstopScraper  # comment out if you don't use it


class ScrapingService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        recommender_service: RecommenderService,
    ):
        self.embedding_service = embedding_service
        self.recommender_service = recommender_service

        # Register all scrapers here
        self.scrapers = [
            InternshalaScraper(),
            UnstopScraper(),  # comment/remove if not ready
        ]

    # ------------------------------------------------------------------
    # NORMAL SCRAPING: DB + FAISS
    # ------------------------------------------------------------------
    def run_all(self, pages_per_source: int = 1) -> int:
        """
        Run all scrapers, store results in DB, build embeddings,
        and update FAISS index.

        Returns:
            int: total new internships stored.
        """
        total_new = 0

        for scraper in self.scrapers:
            current_app.logger.info(
                f"[SCRAPE] Running scraper: {scraper.__class__.__name__} "
                f"for {pages_per_source} pages"
            )
            data: List[Dict] = scraper.scrape(max_pages=pages_per_source)

            for item in data:
                link = item.get("link")
                if not link:
                    continue

                # Skip duplicates
                existing = Internship.query.filter_by(link=link).first()
                if existing:
                    continue

                title = item.get("title", "N/A")
                company = item.get("company", "N/A")
                location = item.get("location", "")
                duration = item.get("duration", "")
                stipend = item.get("stipend", "")
                description = item.get("description", "")
                skills_list = item.get("skills", []) or []
                skills_str = ",".join(skills_list)

                profile_text = (
                    f"Internship Title: {title}. "
                    f"Company: {company}. "
                    f"Location: {location}. "
                    f"Type: {duration}. "
                    f"Stipend offered: {stipend}. "
                    f"Skills required: {', '.join(skills_list)}. "
                    f"Responsibilities: {description}. "
                    f"This internship requires: {', '.join(skills_list)}."
                )

                emb = self.embedding_service.encode_text(profile_text)

                intr = Internship(
                    title=title,
                    company=company,
                    location=location,
                    duration=duration,
                    stipend=stipend,
                    skills=skills_str,
                    description=description,
                    link=link,
                    embedding_json=self.embedding_service.embedding_to_json(emb),
                )

                db.session.add(intr)
                db.session.flush()  # assign id
                self.recommender_service.add_internship_to_index(intr)

                total_new += 1

            db.session.commit()

        current_app.logger.info(f"[SCRAPE] Finished. New internships: {total_new}")
        return total_new

    # ------------------------------------------------------------------
    # HELPERS FOR LIVE SEARCH FILTERING
    # ------------------------------------------------------------------
    def _expand_skill_keywords(self, skills: list[str]) -> list[str]:
        """
        User skills ko normalize + expand karta hai (synonym style).
        e.g. 'MERN' -> ['mern', 'react', 'node', 'express', 'mongodb']
             'cyber security' -> related security keywords
        """
        base = set()

        for s in skills or []:
            s_norm = (s or "").strip().lower()
            if not s_norm:
                continue
            base.add(s_norm)

            # Simple expansions
            if "mern" in s_norm:
                base.update(["mern", "react", "node", "node.js", "express", "mongodb"])
            if "full stack" in s_norm:
                base.update(["full stack", "frontend", "backend"])
            if "cyber security" in s_norm or "cybersecurity" in s_norm:
                base.update(
                    [
                        "cyber security",
                        "cybersecurity",
                        "network security",
                        "information security",
                        "ethical hacking",
                        "penetration testing",
                        "security",
                    ]
                )

        return list(base)

    def _filter_candidates_by_constraints(
        self,
        candidates: list[Dict],
        skills: list[str],
        location_pref: str,
    ) -> list[Dict]:
        """
        Hard filter:
        - Agar skills diye gaye hain -> kam se kam 1 expanded skill keyword
          title/description/skills text me hona chahiye
        - Agar location_pref diya hai -> location string me include hona chahiye
        """
        if not candidates:
            return []

        expanded_skills = self._expand_skill_keywords(skills)
        loc_pref = (location_pref or "").strip().lower()

        filtered: list[Dict] = []

        for item in candidates:
            title = (item.get("title") or "").lower()
            desc = (item.get("description") or "").lower()
            loc = (item.get("location") or "").lower()
            skills_list = item.get("skills", []) or []
            skills_text = " ".join(str(s) for s in skills_list).lower()

            # --- skill condition ---
            skill_ok = True
            if expanded_skills:
                skill_ok = any(
                    key in title or key in desc or key in skills_text
                    for key in expanded_skills
                )

            # --- location condition ---
            loc_ok = True
            if loc_pref:
                loc_ok = loc_pref in loc

            if skill_ok and loc_ok:
                filtered.append(item)

        return filtered

    # ------------------------------------------------------------------
    # LIVE SEARCH: SCRAPE → FILTER → RANK (NO DB WRITE)
    # ------------------------------------------------------------------
    def live_search(
        self,
        profile_text: str,
        skills: list[str],
        location_pref: str,
        interests: str,
        pages_per_source: int = 1,
        top_k: int = 10,
    ) -> list[Dict]:
        """
        Live search:
        - Incremental scraping:
          pages 1, then 2, then 3, ... up to pages_per_source
        - Har step pe:
          - saare candidates collect + de-duplicate (by link)
          - skills + location se HARD FILTER
          - agar filtered >= top_k -> yahi stop
        - Phir filtered list pe hybrid ranking (rank_from_raw)
        """

        max_pages = max(1, pages_per_source)

        # link -> item
        all_candidates_by_link: dict[str, Dict] = {}

        filtered: list[Dict] = []

        for current_pages in range(1, max_pages + 1):
            current_app.logger.info(
                f"[LIVE SEARCH] Scraping up to page {current_pages} "
                f"for each source (max {max_pages})"
            )

            # Scrape each source up to current_pages
            for scraper in self.scrapers:
                data = scraper.scrape(max_pages=current_pages)
                for item in data:
                    link = (item.get("link") or "").strip()
                    if not link:
                        continue
                    # de-duplicate by link
                    all_candidates_by_link[link] = item

            all_candidates = list(all_candidates_by_link.values())
            current_app.logger.info(
                f"[LIVE SEARCH] Total unique candidates so far: {len(all_candidates)}"
            )

            if not all_candidates:
                continue

            # HARD FILTER (skills + location)
            filtered = self._filter_candidates_by_constraints(
                candidates=all_candidates,
                skills=skills,
                location_pref=location_pref,
            )

            current_app.logger.info(
                f"[LIVE SEARCH] After hard filter (page {current_pages}): "
                f"{len(filtered)} candidates"
            )

            # Agar required results mil gaye -> stop scraping further pages
            if len(filtered) >= top_k:
                current_app.logger.info(
                    f"[LIVE SEARCH] Reached desired minimum ({top_k}) filtered results "
                    f"at page {current_pages}, stopping early."
                )
                break

        # Agar max pages ke baad bhi filtered empty hai:
        if not all_candidates_by_link:
            return []

        if not filtered:
            # Strict mode ke liye isko hata sakte ho (tab 0 results milega)
            current_app.logger.info(
                "[LIVE SEARCH] No candidates matched hard filters even after max pages; "
                "falling back to all candidates for ranking."
            )
            filtered = list(all_candidates_by_link.values())

        # Hybrid ranking on filtered pool
        results = self.recommender_service.rank_from_raw(
            profile_text=profile_text,
            skills=skills,
            location_pref=location_pref,
            interests=interests,
            candidates=filtered,
            top_k=top_k,
        )
        return results
