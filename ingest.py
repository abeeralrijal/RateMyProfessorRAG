"""Load raw files from documents/, clean them, chunk them, and write:
    processed/documents.jsonl  -- one cleaned record per source document
    processed/chunks.jsonl     -- documents.jsonl split into chunks ready for embedding

Every cleaned record has the shape:
    {"doc_id": str, "source": str, "type": "review"|"schedule"|"article", "text": str, "metadata": {...}}
Every chunk has the shape:
    {"chunk_id": str, "doc_id": str, "source": str, "type": str, "chunk_index": int, "text": str, "metadata": {...}}
"""
import json
import re
from datetime import datetime
from pathlib import Path

import pdfplumber

DOCS_DIR = Path("documents")
OUT_DOCS_PATH = Path("processed/documents.jsonl")
OUT_CHUNKS_PATH = Path("processed/chunks.jsonl")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Google Maps reviews (clover.json, lanes.json, vie.json, trellis.json)
# ---------------------------------------------------------------------------

def load_reviews(path: Path) -> list[dict]:
    raw = json.loads(path.read_text())
    slug = path.stem
    records = []
    for i, item in enumerate(raw):
        text = item.get("text")
        if not text or not text.strip():
            continue  # star-only ratings with no written review
        records.append({
            "doc_id": f"{slug}-review-{i:02d}",
            "source": f"Google Maps reviews — {item['title']}",
            "type": "review",
            "text": normalize_whitespace(text),
            "metadata": {
                "property": item["title"],
                "reviewer": item.get("name"),
                "stars": item.get("stars"),
                "review_url": item.get("reviewUrl"),
            },
        })
    return records


# ---------------------------------------------------------------------------
# Pre-structured schedule JSON (clovers_schedule.json) — already clean, pass through
# ---------------------------------------------------------------------------

def load_structured_schedule(path: Path) -> list[dict]:
    raw = json.loads(path.read_text())
    records = []
    for item in raw:
        records.append({
            "doc_id": item["id"],
            "source": item["metadata"].get("source", path.stem),
            "type": "schedule",
            "text": normalize_whitespace(item["text"]),
            "metadata": item["metadata"],
        })
    return records


# ---------------------------------------------------------------------------
# Raw tabular schedule PDF (lanes_schedule.pdf) — parse the table, then write it
# in the same narrative style as clovers_schedule.json so both schedules read alike.
# ---------------------------------------------------------------------------

def to_24h(time_str: str) -> str:
    return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")

def parse_schedule_table(table: list[list]) -> dict[str, list[str]]:
    stops = [c for c in table[0] if c]
    per_stop = {stop: [] for stop in stops}
    for row in table[1:]:
        cells = [c for c in row if c]
        if len(cells) != len(stops):
            continue
        for stop, t in zip(stops, cells):
            per_stop[stop].append(t)
    return per_stop


def build_schedule_records(property_name: str, slug: str, service_days: str, days: list[str], per_stop: dict) -> list[dict]:
    records = []
    for stop, times in per_stop.items():
        freq = int((datetime.strptime(times[1], "%I:%M %p") - datetime.strptime(times[0], "%I:%M %p")).total_seconds() / 60)
        text = (
            f"{service_days.capitalize()} ({' and '.join(days) if len(days) < 3 else days[0] + ' through ' + days[-1]}) "
            f"{property_name} Shuttle departures from {stop}: {', '.join(times)}. "
            f"The shuttle leaves every {freq} minutes. "
            f"The first departure is {times[0]} and the last departure is {times[-1]}."
        )
        records.append({
            "doc_id": f"{slug}-shuttle-{service_days}-{slugify(stop)}",
            "source": f"{property_name} Shuttle Schedule",
            "type": "schedule",
            "text": text,
            "metadata": {
                "source": f"{property_name} Shuttle Schedule",
                "type": "schedule",
                "service_days": service_days,
                "days": days,
                "stop": stop,
                "first_departure": to_24h(times[0]),
                "last_departure": to_24h(times[-1]),
                "frequency_minutes": freq,
            },
        })
    return records


def load_lanes_schedule_pdf(path: Path) -> list[dict]:
    with pdfplumber.open(path) as pdf:
        tables = pdf.pages[0].extract_tables()
    weekday = parse_schedule_table(tables[0])
    weekend = parse_schedule_table(tables[1])
    records = build_schedule_records(
        "The Lanes at Union Market", "lanes", "weekday",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], weekday,
    )
    records += build_schedule_records(
        "The Lanes at Union Market", "lanes", "weekend",
        ["Saturday", "Sunday"], weekend,
    )
    return records


# ---------------------------------------------------------------------------
# Prose article PDFs — extract per page, strip known nav/footer boilerplate
# ---------------------------------------------------------------------------

BOILERPLATE_LINES = {
    "Back to Home",
    "Categories",
    "Housing",
    "Was this article helpful?",
}


def clean_article_page(text: str) -> str:
    lines = []
    for ln in text.split("\n"):
        stripped = re.sub(r"^[^\x00-\x7F]+\s*", "", ln.strip())  # drop leading icon-font glyphs (e.g. a "back" arrow icon)
        if stripped not in BOILERPLATE_LINES:
            lines.append(ln)
    return normalize_whitespace("\n".join(lines))


def load_article_pdf(path: Path, source_name: str) -> list[dict]:
    slug = slugify(path.stem)
    records = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = clean_article_page(page.extract_text() or "")
            if not text:
                continue
            records.append({
                "doc_id": f"{slug}-page-{i}",
                "source": source_name,
                "type": "article",
                "text": text,
                "metadata": {"page": i + 1},
            })
    return records


# ---------------------------------------------------------------------------
# Chunking — pack sentences up to CHUNK_SIZE characters, carry CHUNK_OVERLAP
# characters of trailing sentences into the next chunk so a fact sitting at a
# chunk boundary still appears in a neighboring chunk.
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    sentences = split_sentences(text)
    if not sentences:
        return []

    chunks = []
    current: list[str] = []
    current_len = 0

    def current_text():
        return " ".join(current)

    i = 0
    while i < len(sentences):
        s = sentences[i]
        added_len = len(s) + (1 if current else 0)
        if not current or current_len + added_len <= size:
            current.append(s)
            current_len += added_len
            i += 1
            continue

        chunks.append(current_text())

        # carry trailing sentences worth ~`overlap` characters into the next chunk.
        # never carry over the *first* sentence of the finished chunk, so a chunk that
        # was just one long sentence produces an empty overlap and guarantees progress.
        overlap_sentences: list[str] = []
        overlap_len = 0
        for sent in reversed(current[1:]):
            if overlap_sentences and overlap_len + len(sent) > overlap:
                break
            overlap_sentences.insert(0, sent)
            overlap_len += len(sent) + 1
        current = overlap_sentences
        current_len = sum(len(s) + 1 for s in current)

    if current:
        chunks.append(current_text())
    return chunks


def make_chunks(records: list[dict]) -> list[dict]:
    chunks = []
    for r in records:
        pieces = chunk_text(r["text"])
        for idx, piece in enumerate(pieces):
            chunks.append({
                "chunk_id": f"{r['doc_id']}-chunk-{idx}",
                "doc_id": r["doc_id"],
                "source": r["source"],
                "type": r["type"],
                "chunk_index": idx,
                "text": piece,
                "metadata": r["metadata"],
            })
    return chunks


# ---------------------------------------------------------------------------

def load_all_documents() -> list[dict]:
    records = []
    for name in ("clover.json", "lanes.json", "vie.json", "trellis.json"):
        path = DOCS_DIR / name
        if path.exists():
            records += load_reviews(path)
    records += load_structured_schedule(DOCS_DIR / "clovers_schedule.json")
    records += load_lanes_schedule_pdf(DOCS_DIR / "lanes_schedule.pdf")
    records += load_article_pdf(
        DOCS_DIR / "6 Tips for Finding Off-Campus Housing _ Howard University Student Affairs.pdf",
        "Howard University Student Affairs — 6 Tips for Finding Off-Campus Housing",
    )
    records += load_article_pdf(
        DOCS_DIR / "Resources _ Howard University _ Off-Campus Housing Search.pdf",
        "Howard University Student Affairs — Off-Campus Housing Resources FAQ",
    )
    return records


def main():
    records = load_all_documents()
    chunks = make_chunks(records)

    OUT_DOCS_PATH.parent.mkdir(exist_ok=True)
    with OUT_DOCS_PATH.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    with OUT_CHUNKS_PATH.open("w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")

    by_type = {}
    for r in records:
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
    chunk_by_type = {}
    for c in chunks:
        chunk_by_type[c["type"]] = chunk_by_type.get(c["type"], 0) + 1

    print(f"Wrote {len(records)} cleaned documents to {OUT_DOCS_PATH}")
    for t, n in sorted(by_type.items()):
        print(f"  {t}: {n}")
    print(f"Wrote {len(chunks)} chunks to {OUT_CHUNKS_PATH}")
    for t, n in sorted(chunk_by_type.items()):
        print(f"  {t}: {n}")


if __name__ == "__main__":
    main()
