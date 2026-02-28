import os
from pathlib import Path


def load_dotenv_file(path='.env'):
    p = Path(path)
    if not p.exists():
        return
    with p.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


# Load .env from project root if present
load_dotenv_file()

# If running inside Streamlit, prefer `st.secrets` for sensitive values.
try:
    import streamlit as _st
    _secrets = getattr(_st, 'secrets', None)
except Exception:
    _st = None
    _secrets = None


def _get(key, default=None):
    if _secrets and key in _secrets:
        return _secrets[key]
    return os.getenv(key, default)

DB_CONFIG = {
    'dbname': _get('DB_NAME', 'crypto_db'),
    'user': _get('DB_USER', 'postgres'),
    'password': _get('DB_PASSWORD', ''),
    'host': _get('DB_HOST', 'localhost'),
    'port': int(_get('DB_PORT', 5432)),
}
