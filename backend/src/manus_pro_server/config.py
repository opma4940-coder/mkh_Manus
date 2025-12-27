from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

# Repository Root
REPO_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = REPO_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(os.getenv("MANUS_PRO_DB_PATH", str(DATA_DIR / "state.sqlite3")))
FERNET_KEY_PATH = Path(os.getenv("MANUS_PRO_FERNET_KEY_PATH", str(DATA_DIR / "fernet.key")))

# Create data directory if it doesn't exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
FERNET_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

# Workspace - Full access within the repository workspace
WORKSPACE_ROOT = Path(os.getenv("MANUS_PRO_WORKSPACE_ROOT", str(REPO_ROOT / "workspace"))).resolve()
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

OPENMANUS_CONFIG_PATH = Path(os.getenv("OPENMANUS_CONFIG_PATH", str(REPO_ROOT / "config" / "config.toml")))
CEREBRAS_BASE_URL_DEFAULT = os.getenv("CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1")

# API Key Slots
API_KEY_SLOTS = ["api_key_1", "api_key_2", "api_key_3", "api_key_4", "api_key_5"]

# Models
FREE_TIER_MODELS = [
    {"id": "gpt-oss-120b", "context": 65536, "tier": "free", "stage": "production"},
    {"id": "llama-3.3-70b", "context": 65536, "tier": "free", "stage": "production"},
    {"id": "llama3.1-8b", "context": 8192, "tier": "free", "stage": "production"},
    {"id": "qwen-3-235b-a22b-instruct-2507", "context": 65536, "tier": "free", "stage": "preview"},
    {"id": "qwen-3-32b", "context": 65536, "tier": "free", "stage": "production"},
    {"id": "zai-glm-4.6", "context": 64000, "tier": "free", "stage": "preview"},
]

@dataclass(frozen=True)
class AgentProfiles:
    planner_model: str = os.getenv("MANUS_PRO_PLANNER_MODEL", "gpt-oss-120b")
    researcher_model: str = os.getenv("MANUS_PRO_RESEARCHER_MODEL", "llama-3.3-70b")
    coder_model: str = os.getenv("MANUS_PRO_CODER_MODEL", "gpt-oss-120b")
    auditor_model: str = os.getenv("MANUS_PRO_AUDITOR_MODEL", "qwen-3-32b")
    summarizer_model: str = os.getenv("MANUS_PRO_SUMMARIZER_MODEL", "llama3.1-8b")

DEFAULT_AGENT_PROFILES = AgentProfiles()

# Runtime Settings - Optimized for performance and full access
RUNTIME_POLL_INTERVAL_SEC = 0.5 # Faster polling
CYCLE_STEPS_DEFAULT = 10 # More steps per cycle
TOKEN_SOFT_BUDGET_FRACTION = 0.98 # Higher budget utilization
CORS_ALLOWED_ORIGINS = ["*"] # Permissive CORS for local/codespaces use
MAX_FILE_READ_SIZE = 10 * 1024 * 1024 # 10MB file read limit
