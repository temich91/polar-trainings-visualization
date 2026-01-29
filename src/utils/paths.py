from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
PARSER_DIR = SRC_DIR / "parser"
DB_DIR = SRC_DIR / "db"
DATA_DIR = BASE_DIR / "data"
