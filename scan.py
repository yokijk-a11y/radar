import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

import feedparser

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "opportunities.json"

# Public RSS search feeds. These are discovery signals, not proof of demand.
QUERIES = [
    ("Indonesia", '"butuh jasa" OR "mencari jasa" OR "ada yang bisa" Indonesia'),
    ("Indonesia", '"kesulitan" OR "mencari solusi" usaha kecil Indonesia'),
    ("Global", '"looking for" OR "need help" small business service'),
    ("Global", '"looking for a freelancer" OR "hiring freelance" remote'),
    ("AI & Digital", '"AI tool" OR automation small business problem'),
    ("Market", '"supplier needed" OR "looking for supplier" products'),
]
FEEDS = [
    ("Google News", "https://news.google.com/rss/search?q={query}&hl=id&gl=ID&ceid=ID:id"),
    ("Google News", "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"),
]

KEYWORDS = {
    "demand": ["looking for", "need help", "butuh", "mencari", "kesulitan", "need", "wanted", "supplier"],
    "business": ["business", "usaha", "seller", "small business", "umkm", "freelance", "service", "jasa"],
    "digital": ["ai", "automation", "digital", "software", "tool", "online"],
}

def clean(text):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(text or ""))).strip()

def classify(text):
    t = text.lower()
    if any(k in t for k in KEYWORDS["digital"]):
        return "Digital Product / AI"
    if any(k in t for k in ["freelance", "remote", "hiring", "job", "pekerjaan"]):
        return "Remote / Freelance"
    if any(k in t for k in ["supplier", "sourcing", "produk", "product"]):
        return "Market Arbitrage"
    return "Business Opportunity"

def heuristic_score(text):
    t = text.lower()
    score = 25
    score += min(35, sum(7 for k in KEYWORDS["demand"] if k in t))
    score += min(20, sum(5 for k in KEYWORDS["business"] if k in t))
    score += min(10, sum(3 for k in KEYWORDS["digital"] if k in t))
    return min(90, score)

def load_existing():
    if OUT.exists():
        try:
            data = json.loads(OUT.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            pass
    return []

def main():
    existing = load_existing()
    seen = {x.get("id") for x in existing}
    fresh = []
    for market, query in QUERIES:
        lang = "id" if market == "Indonesia" else "en"
        feed_url = FEEDS[0][1].format(query=quote_plus(query)) if lang == "id" else FEEDS[1][1].format(query=quote_plus(query))
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries[:20]:
            title = clean(entry.get("title"))
            summary = clean(entry.get("summary"))
            link = entry.get("link", "")
            if not title or not link:
                continue
            fingerprint = hashlib.sha256((title.lower() + link).encode()).hexdigest()[:16]
            if fingerprint in seen:
                continue
            text = (title + " " + summary).strip()
            fresh.append({
                "id": fingerprint,
                "name": title[:180],
                "category": classify(text),
                "target": market,
                "source": link,
                "source_name": clean(entry.get("source", {}).get("title", "RSS")) or "RSS",
                "evidence": summary[:700],
                "demand": 2,
                "ease": 3,
                "margin": 3,
                "speed": 2,
                "cost": 0,
                "competition": 3,
                "score_hint": heuristic_score(text),
                "status": "New",
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "next": "Buka sumber asli, cek tanggal, dan cari bukti permintaan independen."
            })
            seen.add(fingerprint)

    # Keep newest discoveries first; retain up to 500 records.
    combined = fresh + existing
    combined = combined[:500]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"New items: {len(fresh)} | Total stored: {len(combined)}")

if __name__ == "__main__":
    main()
