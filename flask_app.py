import os

try:
    # python-dotenv is a local-development convenience only: it loads the
    # key/value pairs from a .env file into the environment so config.py's
    # os.environ.get(...) calls pick them up. It is intentionally NOT listed
    # in requirements.txt (Render sets real environment variables through
    # its dashboard instead), so this import is optional.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from application import create_app

app = create_app(os.environ.get("FLASK_CONFIG", "development"))
