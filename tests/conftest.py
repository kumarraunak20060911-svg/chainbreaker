import os
import sys
from pathlib import Path
import tempfile

os.environ.setdefault("CHAINBREAKER_ENVIRONMENT", "test")
os.environ.setdefault("CHAINBREAKER_DATABASE_URL", "sqlite+pysqlite:///runtime/databases/chainbreaker-test.sqlite3")
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
