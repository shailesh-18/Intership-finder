# server.py  (root me)

from app import create_app

# Vercel will look for this "app" variable
app = create_app()
