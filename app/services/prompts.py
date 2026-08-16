from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


@lru_cache
def load(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")