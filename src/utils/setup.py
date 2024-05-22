import os
from dotenv import load_dotenv
from pathlib import Path

from src.auth.firebase import FirebaseObject

load_dotenv()

AUTH_PATH = os.path.join(Path(__file__).parent.parent, "auth", "firebase.json")
"""The path to the Firebase authentication file."""

FIREBASE = FirebaseObject.from_json(AUTH_PATH, options={"storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET")})
"""The Firebase object used for accessing the Firebase API."""

STORAGE_CLIENT = FIREBASE.storage_client
"""The file storage client used for accessing the Firebase API."""
