from .db import db
from sqlalchemy import UniqueConstraint

class Internship(db.Model):
    __tablename__ = "internships"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    company = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(256), nullable=True)
    duration = db.Column(db.String(256), nullable=True)
    stipend = db.Column(db.String(256), nullable=True)   # ← NEW FIELD
    skills = db.Column(db.String(512), nullable=True)
    description = db.Column(db.Text, nullable=True)
    link = db.Column(db.String(512), nullable=False, unique=True)
    embedding_json = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "duration": self.duration,
            "stipend": self.stipend,             # ← NEW FIELD
            "skills": self.skills.split(",") if self.skills else [],
            "description": self.description,
            "link": self.link,
        }

# class Internship(db.Model):
#     __tablename__ = "internships"

#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(256), nullable=False)
#     company = db.Column(db.String(256), nullable=False)
#     location = db.Column(db.String(256), nullable=True)
#     duration = db.Column(db.String(256), nullable=True)
#     skills = db.Column(db.String(512), nullable=True)  # comma-separated
#     description = db.Column(db.Text, nullable=True)
#     link = db.Column(db.String(512), nullable=False, unique=True)
#     stipend = db.Column(db.String(256), nullable=True)

#     # Store embedding as a JSON string of floats (for rebuilding FAISS)
#     embedding_json = db.Column(db.Text, nullable=True)

#     __table_args__ = (
#         UniqueConstraint("link", name="uq_internship_link"),
#     )

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "title": self.title,
#             "company": self.company,
#             "location": self.location,
#             "duration": self.duration,
#             "skills": self.skills.split(",") if self.skills else [],
#             "description": self.description,
#             "link": self.link,
#         }
