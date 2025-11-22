# import os

# BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# class Config:
#     SQLALCHEMY_DATABASE_URI = (
#         "sqlite:///" + os.path.join(BASE_DIR, "internships.db")
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     JSON_SORT_KEYS = False
#     SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """
    Config works like this:

    1. If DATABASE_URL is set (env var) -> use that
       - e.g. postgres://user:pass@host:5432/dbname
    2. Else if running on Vercel (VERCEL env set) -> use SQLite in /tmp
       - sqlite:////tmp/internships.db   (ephemeral per instance)
    3. Else (local dev) -> use SQLite file in project folder
       - sqlite:///<BASE_DIR>/internships.db
    """

    # 1) Try DATABASE_URL from env (prod / external DB)
    _db_url = os.getenv("DATABASE_URL")

    if not _db_url:
        # detect vercel environment
        if os.getenv("VERCEL"):
            # 2) Vercel: use /tmp (only writable dir), ephemeral
            _db_url = "sqlite:////tmp/internships.db"
        else:
            # 3) Local dev: file in project directory
            _db_path = os.path.join(BASE_DIR, "internships.db")
            _db_url = "sqlite:///" + _db_path

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
