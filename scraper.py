import json
import re

import requests

BASE_URL = "https://superkalam.com/upsc-prelims/previous-year-question-paper/{year}/gs-analysis/{subject}"

SUBJECTS = {
    "Economy": "economy",
    "Geography": "geography",
    "Indian Polity": "indian-polity",
    "Environment & Ecology": "environment-and-ecology",
    "Science & Technology": "science-and-technology",
    "International Relations": "international-relations",
    "Art & Culture": "art-and-culture",
    "Medieval History": "medieval-history",
    "Modern History": "modern-history",
    "Ancient History": "ancient-history",
    "Social Issues & Schemes": "social-issues-and-schemes",
}


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def get_subject_aliases(subject_display: str) -> set:
    extra_subject_names = {
        "Geography": {"Indian Geography", "World Geography", "Physical Geography"},
    }
    names = {subject_display}
    names.update(extra_subject_names.get(subject_display, set()))
    return {x.strip().lower() for x in names}


def get_options(options_raw) -> dict:
    options = {}
    if not isinstance(options_raw, list):
        return options

    for idx, item in enumerate(options_raw):
        key = chr(ord("A") + idx)
        if isinstance(item, str):
            options[key] = item.strip()
        elif isinstance(item, dict):
            text = (
                item.get("option")
                or item.get("value")
                or item.get("text")
                or item.get("title")
                or ""
            )
            options[key] = str(text).strip()
    return {k: v for k, v in options.items() if v}


def get_answer_key(answer_raw: str, options: dict) -> str | None:
    if not answer_raw:
        return None
    m = re.search(r"\b([A-D])\b", answer_raw, re.IGNORECASE)
    if m:
        return m.group(1).upper()

    ans_norm = answer_raw.strip().lower()
    for key, text in options.items():
        if text.strip().lower() == ans_norm:
            return key
    return None


def parse_questions(html: str, subject_display: str) -> list:
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError("Could not find page data in response.")

    data = json.loads(m.group(1))
    content_blocks = (
        data.get("props", {})
        .get("pageProps", {})
        .get("blog", {})
        .get("content", [])
    )

    mcq_block = next(
        (
            block
            for block in content_blocks
            if isinstance(block, dict)
            and block.get("__component") == "ui-components.mcq-uuid"
        ),
        None,
    )
    if not mcq_block:
        return []

    subject_aliases = get_subject_aliases(subject_display)
    questions = []
    for idx, mcq in enumerate(mcq_block.get("mcqs", []), start=1):
        mcq_subjects = {
            (s.get("name", "").strip().lower() if isinstance(s, dict) else str(s).strip().lower())
            for s in mcq.get("subjects", [])
        }
        if mcq_subjects and subject_aliases.isdisjoint(mcq_subjects):
            continue

        options = get_options(mcq.get("options", []))
        answer_key = get_answer_key(str(mcq.get("answer", "")), options)

        questions.append(
            {
                "number": idx,
                "difficulty": str(mcq.get("difficulty", "")).capitalize(),
                "question": str(mcq.get("question", "")).strip(),
                "options": options,
                "answer": answer_key,
                "explanation": str(mcq.get("explanation", "")).strip(),
            }
        )

    return questions


def scrape(year: int, subject_display: str):
    slug = SUBJECTS[subject_display]
    url  = BASE_URL.format(year=year, subject=slug)
    html = fetch_html(url)
    questions = parse_questions(html, subject_display)
    return questions, url