# import random
# import time
# from typing import List, Dict

# import requests
# from bs4 import BeautifulSoup

# from .base import BaseScraper


# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#     "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
#     "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
# ]


# class InternshalaScraper(BaseScraper):
#     BASE_URL = "https://internshala.com/internships"

#     def _get(self, url: str, retries: int = 3, timeout: int = 10) -> requests.Response:
#         for attempt in range(retries):
#             try:
#                 headers = {
#                     "User-Agent": random.choice(USER_AGENTS),
#                     "Accept-Language": "en-US,en;q=0.9",
#                 }
#                 resp = requests.get(url, headers=headers, timeout=timeout)
#                 if resp.status_code == 200:
#                     return resp
#             except requests.RequestException:
#                 pass
#             time.sleep(1 + attempt)
#         raise RuntimeError(f"Failed to fetch URL: {url}")

#     def scrape(self, max_pages: int = 1) -> List[Dict]:
#         """Very basic Internshala scraper (may need selector updates over time)."""
#         internships: List[Dict] = []

#         for page in range(1, max_pages + 1):
#             url = f"{self.BASE_URL}/page-{page}"
#             resp = self._get(url)
#             soup = BeautifulSoup(resp.text, "html.parser")

#             cards = soup.select("div.individual_internship")
#             if not cards:
#                 break

#             for card in cards:
#                 try:
#                     title_el = card.select_one("h3 a")
#                     company_el = card.select_one("a.link_display_like_text")
#                     location_el = card.select_one("p.location_link")
#                     duration_el = card.select_one("div.item_body span")
#                     desc_el = card.select_one("div.about_company")
#                     link_el = title_el

#                     title = title_el.get_text(strip=True) if title_el else "N/A"
#                     company = company_el.get_text(strip=True) if company_el else "N/A"
#                     location = location_el.get_text(strip=True) if location_el else ""
#                     duration = duration_el.get_text(strip=True) if duration_el else ""
#                     description = desc_el.get_text(strip=True) if desc_el else ""

#                     link = (
#                         "https://internshala.com"
#                         + link_el.get("href", "")
#                         if link_el and link_el.get("href")
#                         else ""
#                     )

#                     # skills may not always be clearly marked; basic example:
#                     skills_els = card.select("div.tags span")
#                     skills = [s.get_text(strip=True) for s in skills_els]

#                     internships.append(
#                         {
#                             "title": title,
#                             "company": company,
#                             "location": location,
#                             "duration": duration,
#                             "skills": skills,
#                             "description": description,
#                             "link": link,
#                         }
#                     )
#                 except Exception:
#                     # ignore broken card
#                     continue

#             time.sleep(random.uniform(1.0, 2.5))

#         return internships
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


class InternshalaScraper(BaseScraper):
    BASE_URL = "https://internshala.com/internships"

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
            # simple backoff
            time.sleep(1 + attempt)
        raise RuntimeError(f"Failed to fetch URL: {url}")

    def scrape(self, max_pages: int = 1) -> List[Dict]:
        """
        Scrape Internshala internships.
        NOTE: This is for learning/demo. Always respect robots.txt & TOS.
        """
        internships: List[Dict] = []

        for page in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/page-{page}"
            resp = self._get(url)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Each card matches your HTML: div.container-fluid.individual_internship...
            cards = soup.select("div.individual_internship")
            if not cards:
                break

            for card in cards:
                try:
                    # ---------- Title ----------
                    title_el = card.select_one(
                        "h3.job-internship-name a.job-title-href"
                    )
                    title = title_el.get_text(strip=True) if title_el else "N/A"

                    # ---------- Company ----------
                    company_el = card.select_one("p.company-name")
                    company = company_el.get_text(strip=True) if company_el else "N/A"

                    # ---------- Location ----------
                    # <div class="row-1-item locations"> ... <a>Mumbai</a>
                    location_el = card.select_one(
                        "div.row-1-item.locations span a"
                    )
                    location = (
                        location_el.get_text(strip=True) if location_el else ""
                    )

                    # ---------- Duration ----------
                    # Find the row-1-item that has calendar icon
                    duration = ""
                    row_items = card.select("div.detail-row-1 div.row-1-item")
                    for row in row_items:
                        icon = row.select_one("i.ic-16-calendar")
                        if icon:
                            span = row.select_one("span")
                            if span:
                                duration = span.get_text(strip=True)
                            break
                    # ---------- Stipend ----------
                    stipend = ""
                    for row in row_items:
                        icon = row.select_one("i.ic-16-money")
                        if icon:
                            span = row.select_one("span.stipend")
                            if span:
                                stipend = span.get_text(strip=True)
                            break


                    # ---------- Description ----------
                    # <div class="about_job"><div class="text">...</div></div>
                    desc_el = card.select_one("div.about_job div.text")
                    description = (
                        desc_el.get_text(strip=True) if desc_el else ""
                    )

                    # ---------- Skills ----------
                    # <div class="job_skills"><div class="job_skill">Adobe Photoshop</div>...</div>
                    skills_els = card.select("div.job_skills div.job_skill")
                    skills = [s.get_text(strip=True) for s in skills_els]

                    # ---------- Link ----------
                    link_el = title_el
                    if link_el and link_el.get("href"):
                        href = link_el.get("href")
                        if href.startswith("http"):
                            link = href
                        else:
                            link = "https://internshala.com" + href
                    else:
                        link = ""

                    if not link:
                        # skip if we don't have a unique link
                        continue

                    # internships.append(
                    #     {
                    #         "title": title,
                    #         "company": company,
                    #         "location": location,
                    #         "duration": duration,
                    #         "skills": skills,
                    #         "description": description,
                    #         "link": link,
                    #     }
                    # )
                    internships.append(
    {
        "title": title,
        "company": company,
        "location": location,
        "duration": duration,
        "stipend": stipend,     # ← NEW FIELD
        "skills": skills,
        "description": description,
        "link": link,
    }
)

                except Exception:
                    # ignore card if anything breaks (HTML changed etc.)
                    continue

            # Be polite – small delay between pages
            time.sleep(random.uniform(1.0, 2.5))

        return internships
