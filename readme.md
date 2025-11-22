# Internship Finder – Free, Local Internship Recommendation Engine

Internship Finder is a 100% free, self-hosted web app that:

- Scrapes internships from public job boards (e.g., Internshala, Unstop\*).
- Stores them in a local SQLite database.
- Generates text embeddings using free Hugging Face models.
- Uses FAISS + a hybrid scoring engine (vector similarity + skills + location) to recommend the best matches.

Everything runs locally using open-source tools – no paid APIs, no OpenAI, no Gemini, no Claude.

> \*Always verify each website’s Terms of Service and robots.txt before scraping. This project is for learning/demo purposes.


---

## ✨ Key Features

- **Flask backend** with modular structure (`routes/`, `services/`, `scrapers/`, `models/`, `utils/`).
- **Two recommendation modes:**
  - **DB Recommendations** (`/`): scrape once → build index → recommend from stored internships.
  - **Live Search** (`/live`): take user requirements → scrape targeted pages in real time → filter + rank only relevant internships.
- **Free web scraping** using `requests` + `BeautifulSoup` (and optionally Selenium/Playwright if you add it).
- **Open-source embeddings** via sentence-transformers (e.g. `all-MiniLM-L6-v2`).
- **FAISS vector search** for fast similarity search on embeddings.
- **Hybrid ranking algorithm** combining:
  - Embedding similarity (semantic match).
  - Skill overlap.
  - Location match.
  - Interest keyword match.
- **Simple web UI**:
  - Trigger scraping.
  - Fill profile (skills, interests, location, experience).
  - See recommended internships as nice cards with title, company, location, duration, stipend, skills, and score.
- **Purely local / free stack** – easy to run on a laptop and deploy to free services (Render/Fly.io/etc.) if you want.


---

## 🏗 Project Structure

```bash
internship_finder/
  main.py                  # Flask entrypoint
  requirements.txt
  app/
    __init__.py            # create_app, service wiring
    config.py              # configuration (DB URL, model name, etc.)
    models/
      __init__.py
      db.py                # SQLAlchemy db object
      internship.py        # Internship model
    routes/
      api.py               # API + UI routes
    services/
      __init__.py          # exports services
      embedding_service.py # HuggingFace embeddings
      recommender_service.py # FAISS + hybrid scoring
      scraping_service.py  # runs all scrapers + live search
    scrapers/
      base.py              # BaseScraper interface
      internshala.py       # Internshala scraper
      unstop.py            # Unstop scraper (or any HTML board you plug in)
      # your_other_source.py
    templates/
      index.html           # DB-based recommendations UI
      live_search.html     # Live scrape + search UI
    static/
      css/
        style.css          # shared styling
      js/
        app.js             # logic for index.html
        live.js            # logic for live_search.html
  linkedin_internships.csv # optional CSV import for manual sources
  import_linkedin_csv.py   # example importer from CSV to DB
