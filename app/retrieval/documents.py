"""Each short KB article is one chunk, preserving complete policy rules."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

KB_DIRECTORY = Path(__file__).resolve().parents[2] / "kb"


@dataclass(frozen=True)
class Chunk:
    source_id: str
    title: str
    text: str
    version: str
    audience: str


def load_chunks(directory: Path = KB_DIRECTORY) -> list[Chunk]:
    chunks = []
    for path in sorted(directory.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        match = re.fullmatch(
            r"# ([^\n]+)\n\nAudience: (public|internal)\n\n(.+)", content, re.DOTALL
        )
        if not re.fullmatch(r"KB-[A-Z]+-\d{3}", path.stem) or not match:
            raise ValueError(f"Invalid KB article format: {path.name}")
        title, audience, body = match.groups()
        chunks.append(Chunk(
            path.stem, title, body, sha256(content.encode()).hexdigest(), audience
        ))
    if not chunks:
        raise ValueError("No KB articles found; refusing to replace the index")
    return chunks
