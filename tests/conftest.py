import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT / "website", ROOT / "tools", ROOT / "18-mock-examinations" / "engine", ROOT / "19-hands-on-labs" / "common"):
    sys.path.insert(0, str(p))
