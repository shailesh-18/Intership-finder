from app import create_app
# from app.utils.logging_utils import setup_logging


# setup_logging()   # optional
app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
