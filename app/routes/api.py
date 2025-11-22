# from flask import Blueprint, request, jsonify, current_app

# from ..models.internship import Internship
# from ..models.db import db
# from ..services.scraping_service import ScrapingService
# from ..services.embedding_service import EmbeddingService
# from ..services.recommender_service import RecommenderService


# api_bp = Blueprint("api", __name__)


# def _get_services() -> tuple[EmbeddingService, RecommenderService]:
#     # Services were stored in app.extensions in create_app()
#     emb_svc: EmbeddingService = current_app.extensions["embedding_service"]
#     rec_svc: RecommenderService = current_app.extensions["recommender_service"]
#     return emb_svc, rec_svc


# @api_bp.route("/health", methods=["GET"])
# def health():
#     return jsonify({"status": "ok"}), 200


# @api_bp.route("/scrape", methods=["GET"])
# def scrape():
#     pages = int(request.args.get("pages", 1))
#     emb_svc, rec_svc = _get_services()

#     scraping_service = ScrapingService(emb_svc, rec_svc)
#     new_count = scraping_service.run_all(pages_per_source=pages)

#     return jsonify({"message": "Scraping completed", "new_internships": new_count})


# @api_bp.route("/internships", methods=["GET"])
# def list_internships():
#     limit = int(request.args.get("limit", 50))
#     offset = int(request.args.get("offset", 0))

#     query = Internship.query.order_by(Internship.id.desc())
#     total = query.count()
#     items = query.offset(offset).limit(limit).all()

#     return jsonify(
#         {
#             "total": total,
#             "offset": offset,
#             "limit": limit,
#             "items": [i.to_dict() for i in items],
#         }
#     )


# @api_bp.route("/recommend", methods=["POST"])
# def recommend():
#     """
#     Expected JSON:
#     {
#       "skills": ["python", "flask"],
#       "interests": "web dev, ai",
#       "location_preference": "remote or Mumbai",
#       "experience_level": "beginner",
#       "top_k": 10
#     }
#     """
#     data = request.get_json(force=True) or {}

#     skills = data.get("skills", [])
#     interests = data.get("interests", "")
#     location_pref = data.get("location_preference", "")
#     experience = data.get("experience_level", "")
#     top_k = int(data.get("top_k", 10))

#     profile_text = (
#         f"Skills: {', '.join(skills)}. "
#         f"Interests: {interests}. "
#         f"Preferred location: {location_pref}. "
#         f"Experience level: {experience}."
#     )

#     _, rec_svc = _get_services()
#     results = rec_svc.recommend(profile_text, top_k=top_k)

#     return jsonify({"profile_text": profile_text, "results": results})
# app/routes/api.py

from flask import Blueprint, request, jsonify, current_app
from flask import Blueprint, request, jsonify, current_app, render_template


from ..models.internship import Internship
from ..models.db import db
from ..services.scraping_service import ScrapingService
from ..services.embedding_service import EmbeddingService
from ..services.recommender_service import RecommenderService


api_bp = Blueprint("api", __name__)


def _get_services() -> tuple[EmbeddingService, RecommenderService]:
    emb_svc: EmbeddingService = current_app.extensions["embedding_service"]
    rec_svc: RecommenderService = current_app.extensions["recommender_service"]
    return emb_svc, rec_svc


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@api_bp.route("/", methods=["GET"])
def home():
    # Serve the main HTML UI
    return render_template("index.html")

@api_bp.route("/live", methods=["GET"])
def live_page():
    return render_template("live_search.html")

@api_bp.route("/scrape", methods=["GET"])
def scrape():
    pages = int(request.args.get("pages", 1))
    emb_svc, rec_svc = _get_services()

    scraping_service = ScrapingService(emb_svc, rec_svc)
    new_count = scraping_service.run_all(pages_per_source=pages)

    return jsonify({"message": "Scraping completed", "new_internships": new_count})


@api_bp.route("/internships", methods=["GET"])
def list_internships():
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    query = Internship.query.order_by(Internship.id.desc())
    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return jsonify(
        {
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": [i.to_dict() for i in items],
        }
    )


@api_bp.route("/recommend", methods=["POST"])
# def recommend():
#     data = request.get_json(force=True) or {}

#     skills = data.get("skills", [])
#     interests = data.get("interests", "")
#     location_pref = data.get("location_preference", "")
#     experience = data.get("experience_level", "")
#     top_k = int(data.get("top_k", 10))

#     # profile_text = (
#     #     f"Skills: {', '.join(skills)}. "
#     #     f"Interests: {interests}. "
#     #     f"Preferred location: {location_pref}. "
#     #     f"Experience level: {experience}."
#     # )
#     profile_text = (
#     f"I am looking for internships that match my profile. "
#     f"My skills include: {', '.join(skills)}. "
#     f"My interests are: {interests}. "
#     f"My preferred location is: {location_pref}. "
#     f"My experience level is: {experience}. "
#     f"I want internships highly relevant to these skills and interests. "
# )


#     _, rec_svc = _get_services()
#     results = rec_svc.recommend(profile_text, top_k=top_k)

#     return jsonify({"profile_text": profile_text, "results": results})
@api_bp.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json(force=True) or {}

    skills = data.get("skills", []) or []
    interests = data.get("interests", "") or ""
    location_pref = data.get("location_preference", "") or ""
    experience = data.get("experience_level", "") or ""
    top_k = int(data.get("top_k", 10))

    # Stronger profile text for embeddings
    profile_text = (
        "I am looking for internships that match my profile. "
        f"My skills include: {', '.join(skills)}. "
        f"My interests are: {interests}. "
        f"My preferred location is: {location_pref}. "
        f"My experience level is: {experience}. "
        "Please find internships that are highly relevant to these skills, interests, and location."
    )

    emb_svc, rec_svc = _get_services()
    results = rec_svc.recommend(
        profile_text=profile_text,
        skills=skills,
        location_pref=location_pref,
        interests=interests,
        top_k=top_k,
    )

    return jsonify({"profile_text": profile_text, "results": results})

@api_bp.route("/live-search", methods=["POST"])
def live_search():
    data = request.get_json(force=True) or {}

    skills = data.get("skills", []) or []
    interests = data.get("interests", "") or ""
    location_pref = data.get("location_preference", "") or ""
    experience = data.get("experience_level", "") or ""
    top_k = int(data.get("top_k", 10))
    pages = int(data.get("pages", 1))

    profile_text = (
        "I am looking for internships that match my profile. "
        f"My skills include: {', '.join(skills)}. "
        f"My interests are: {interests}. "
        f"My preferred location is: {location_pref}. "
        f"My experience level is: {experience}. "
        "Please find internships that are highly relevant to these skills, interests, and location."
    )

    emb_svc, rec_svc = _get_services()
    scraping_service = ScrapingService(emb_svc, rec_svc)

    results = scraping_service.live_search(
        profile_text=profile_text,
        skills=skills,
        location_pref=location_pref,
        interests=interests,
        pages_per_source=pages,
        top_k=top_k,
    )

    return jsonify(
        {
            "profile_text": profile_text,
            "results": results,
            "pages_per_source": pages,
        }
    )
