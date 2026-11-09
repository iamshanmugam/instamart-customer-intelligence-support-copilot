from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_KB = PROJECT_ROOT / "data" / "knowledge_base"
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "Instamart_DB.sqlite"
OUTPUTS = PROJECT_ROOT / "outputs"
OUTPUTS_EDA = OUTPUTS / "eda"
OUTPUTS_SEGMENTATION = OUTPUTS / "segmentation"
OUTPUTS_TICKET = OUTPUTS / "ticket_triage"
OUTPUTS_RAG = OUTPUTS / "rag"
MODELS_DIR = PROJECT_ROOT / "models"
INSTRUCTOR_DIR = PROJECT_ROOT / "instructor-materials"

RANDOM_SEED = 42
