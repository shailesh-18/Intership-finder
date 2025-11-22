import random
import time
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]


class UnstopScraper(BaseScraper):
    """
    Scraper template for Unstop internships listing.

    IMPORTANT:
    - Use only on pages you are allowed to scrape (robots.txt / TOS).
    - Unstop is an Angular app; this works only if HTML is server-rendered
      or view-source / network HTML contains these tags.
    """

    BASE_URL = "https://unstop.com/internships"  # main listing

    def _get(self, url: str, retries: int = 3, timeout: int = 10) -> requests.Response:
        for attempt in range(retries):
            try:
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept-Language": "en-US,en;q=0.9",
                }
                resp = requests.get(url, headers=headers, timeout=timeout)
                if resp.status_code == 200:
                    return resp
            except requests.RequestException:
                pass
            time.sleep(1 + attempt)
        raise RuntimeError(f"Failed to fetch URL: {url}")

    def scrape(self, max_pages: int = 1) -> List[Dict]:
        internships: List[Dict] = []

        for page in range(1, max_pages + 1):
            # pagination pattern may differ; adjust if needed
            # e.g., https://unstop.com/internships?oppstatus=open&page=2 etc.
            url = f"{self.BASE_URL}?page={page}"
            resp = self._get(url)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Each internship card like:
            # <app-competition-listing ...>
            #   <a class="item opp_..."> ... </a>
            cards = soup.select("app-competition-listing a.item")
            if not cards:
                # No more cards found – probably end of listing
                break

            for card in cards:
                try:
                    # ---------- Title ----------
                    title_el = card.select_one("h2.double-wrap")
                    title = title_el.get_text(strip=True) if title_el else "N/A"

                    # ---------- Company ----------
                    company_el = card.select_one("p.single-wrap")
                    company = company_el.get_text(strip=True) if company_el else "N/A"

                    # ---------- Basic fields container ----------
                    # This section has things like:
                    # - No prior experience required
                    # - Remote
                    # - Part Time
                    # - stipend
                    other_fields = card.select_one("div.other_fields")
                    location_parts: list[str] = []
                    work_type = ""
                    experience_text = ""
                    stipend = ""

                    if other_fields:
                        # Iterate over each child block inside other_fields
                        info_divs = other_fields.select("div.ng-star-inserted")
                        for div in info_divs:
                            text = " ".join(
                                s.get_text(" ", strip=True) for s in div.select("span")
                            ).strip()
                            if not text:
                                continue

                            # Heuristics based on your snippet
                            if "Applied" in text:
                                continue
                            elif "experience" in text.lower():
                                experience_text = text
                            elif "Part Time" in text or "Full Time" in text:
                                work_type = text
                            elif "/Month" in text or "month" in text.lower():
                                # This is likely stipend block
                                stipend = text
                            elif any(
                                kw in text
                                for kw in ["Remote", "Delhi", "Bangalore", "Mumbai"]
                            ):
                                location_parts.append(text)
                            else:
                                # might be some other label; ignore for now
                                pass

                    location = ", ".join(dict.fromkeys(location_parts))  # unique order

                    # ---------- Skills ----------
                    # From: <div class="center-bullet"><div class="align-center flex-wrap ...">
                    skill_spans = card.select(
                        "div.center-bullet div.align-center span.font-12"
                    )
                    skills = [s.get_text(strip=True) for s in skill_spans]

                    # ---------- Eligibility chips (optional skills) ----------
                    # From: <div class="skill_list"> ... <span class="chip_text">Undergraduate</span> ...
                    chip_spans = card.select("div.skill_list span.chip_text")
                    chip_texts = [c.get_text(strip=True) for c in chip_spans]
                    # We can append them as extra "skills"
                    for c in chip_texts:
                        if c and c not in skills:
                            skills.append(c)

                    # ---------- Description ----------
                    # Listing card itself doesn't show full description; we keep it empty here.
                    description = ""
                    if experience_text:
                        description = experience_text

                    # ---------- Link ----------
                    href = card.get("href", "").strip()
                    if not href:
                        continue

                    if href.startswith("http"):
                        link = href
                    else:
                        link = "https://unstop.com" + href

                    internships.append(
                        {
                            "title": title,
                            "company": company,
                            "location": location,
                            "duration": work_type,  # or keep separate; here we store work_type in duration
                            "stipend": stipend,
                            "skills": skills,
                            "description": description,
                            "link": link,
                        }
                    )

                except Exception:
                    # If anything breaks for this card, skip it
                    continue

            time.sleep(random.uniform(1.0, 2.0))

        return internships
