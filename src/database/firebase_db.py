from pathlib import Path
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, firestore

_app_initialized = False

def init_firebase(credentials_path: str) -> None:
    global _app_initialized
    if _app_initialized:
        return
    cred_path = Path(credentials_path)
    if not cred_path.exists():
        raise FileNotFoundError(f"Firebase credentials not found: {credentials_path}")
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)
    _app_initialized = True

def push_document(collection: str, doc: Dict[str, Any], credentials_path: Optional[str] = None) -> str:
    if not _app_initialized and credentials_path:
        init_firebase(credentials_path)
    db = firestore.client()
    ref = db.collection(collection).add(doc)
    return ref[1].id