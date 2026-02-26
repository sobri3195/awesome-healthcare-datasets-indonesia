#!/usr/bin/env python3
"""Fetch 1000+ healthcare-related repositories from GitHub Search API.

Outputs:
- data/github_healthcare_repositories.csv
- data/github_healthcare_summary.md
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from collections import Counter, OrderedDict
from typing import Dict, Iterable, List

DEFAULT_QUERIES = [
    '"healthcare dataset" in:name,description,readme',
    '"medical dataset" in:name,description,readme',
    '"hospital dataset" in:name,description,readme',
    '"simrs" in:name,description,readme',
    '"obat" "dataset" indonesia in:name,description,readme',
    '"kardiovaskular" dataset in:name,description,readme',
    '"indonesia health" dataset in:name,description,readme',
    '"rekam medis" dataset in:name,description,readme',
]


def classify_category(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["simrs", "hospital information system", "rekam medis", " his "]):
        return "SIMRS"
    if any(k in t for k in ["obat", "drug", "pharmaceutical", "farmasi", "medicine"]):
        return "Obat"
    if any(k in t for k in ["kardi", "cardio", "heart", "ecg", "ekg"]):
        return "Kardiovaskular"
    return "General Healthcare"


def github_search(query: str, page: int, per_page: int) -> Dict:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page,
        }
    )
    url = f"https://api.github.com/search/repositories?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "awesome-healthcare-datasets-indonesia-bot",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_repositories(
    queries: Iterable[str], target: int, max_pages: int, per_page: int, sleep_seconds: float
) -> List[Dict]:
    repos: "OrderedDict[str, Dict]" = OrderedDict()

    for query in queries:
        for page in range(1, max_pages + 1):
            payload = github_search(query=query, page=page, per_page=per_page)
            items = payload.get("items", [])
            if not items:
                break

            for item in items:
                full_name = item.get("full_name")
                if not full_name:
                    continue

                description = (item.get("description") or "").replace("\n", " ").strip()
                topics = item.get("topics") or []
                topics_text = ",".join(topics)
                classify_text = f"{item.get('name', '')} {description} {topics_text}"

                repos[full_name] = {
                    "source_query": query,
                    "name": item.get("name", ""),
                    "full_name": full_name,
                    "url": item.get("html_url", ""),
                    "category": classify_category(classify_text),
                    "description": description,
                    "language": item.get("language") or "",
                    "stars": item.get("stargazers_count", 0),
                    "forks": item.get("forks_count", 0),
                    "open_issues": item.get("open_issues_count", 0),
                    "created_at": item.get("created_at", ""),
                    "updated_at": item.get("updated_at", ""),
                    "topics": topics_text,
                }

            print(f"[INFO] query={query!r} page={page} unique_repos={len(repos)}")
            if len(repos) >= target:
                return list(repos.values())
            time.sleep(sleep_seconds)

    return list(repos.values())


def write_csv(rows: List[Dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows:
        with open(path, "w", encoding="utf-8", newline="") as file:
            file.write("\n")
        return

    fieldnames = [
        "source_query",
        "name",
        "full_name",
        "url",
        "category",
        "description",
        "language",
        "stars",
        "forks",
        "open_issues",
        "created_at",
        "updated_at",
        "topics",
    ]
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: List[Dict], path: str, target: int) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    by_category = Counter(row["category"] for row in rows)
    by_language = Counter((row["language"] or "Unknown") for row in rows)
    top_starred = sorted(rows, key=lambda r: int(r["stars"]), reverse=True)[:20]

    with open(path, "w", encoding="utf-8") as file:
        file.write("# Ringkasan Pengumpulan GitHub Healthcare Repositories\n\n")
        file.write(f"- Target entri: **{target}**\n")
        file.write(f"- Total entri terkumpul: **{len(rows)}**\n\n")

        file.write("## Distribusi Kategori\n")
        for category, count in by_category.most_common():
            file.write(f"- {category}: {count}\n")

        file.write("\n## Top Bahasa Pemrograman\n")
        for language, count in by_language.most_common(15):
            file.write(f"- {language}: {count}\n")

        file.write("\n## Top 20 Repository Berdasarkan Stars\n")
        for row in top_starred:
            file.write(f"- [{row['full_name']}]({row['url']}) — ⭐ {row['stars']} — {row['category']}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch healthcare dataset repositories from GitHub")
    parser.add_argument("--target", type=int, default=1200, help="Target number of unique repositories")
    parser.add_argument("--max-pages", type=int, default=10, help="Max page per query (GitHub cap: 10)")
    parser.add_argument("--per-page", type=int, default=100, help="Items per page")
    parser.add_argument("--sleep", type=float, default=2.0, help="Sleep between requests (seconds)")
    parser.add_argument(
        "--csv-output",
        default="data/github_healthcare_repositories.csv",
        help="Output CSV path",
    )
    parser.add_argument(
        "--summary-output",
        default="data/github_healthcare_summary.md",
        help="Output summary markdown path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        rows = fetch_repositories(
            queries=DEFAULT_QUERIES,
            target=args.target,
            max_pages=args.max_pages,
            per_page=args.per_page,
            sleep_seconds=args.sleep,
        )
    except Exception as exc:
        print(f"[ERROR] Fetch failed: {exc}")
        return 1

    write_csv(rows, args.csv_output)
    write_summary(rows, args.summary_output, args.target)

    print(f"[DONE] Collected {len(rows)} repositories")
    print(f"[DONE] CSV: {args.csv_output}")
    print(f"[DONE] Summary: {args.summary_output}")

    if len(rows) < args.target:
        print("[WARN] Target not reached. Add more queries or rerun with broader keywords.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
