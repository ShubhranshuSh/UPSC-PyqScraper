import argparse
import json
from pathlib import Path

from scraper import SUBJECTS, scrape


def run_batch(start_year: int, end_year: int, subjects: list[str], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    total_files = 0
    total_questions = 0

    for year in range(start_year, end_year + 1):
        year_dir = out_dir / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)

        for subject in subjects:
            try:
                questions, url = scrape(year, subject)
            except Exception as exc:
                print(f"[ERROR] {year} | {subject}: {exc}")
                continue

            payload = {
                "year": year,
                "subject": subject,
                "source_url": url,
                "question_count": len(questions),
                "questions": questions,
            }
            file_name = f"{subject.lower().replace('&', 'and').replace(' ', '_')}.json"
            file_path = year_dir / file_name
            file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

            print(f"[OK] {year} | {subject}: {len(questions)} questions")
            total_files += 1
            total_questions += len(questions)

    print("-" * 60)
    print(f"Done. Files created: {total_files}")
    print(f"Total questions scraped: {total_questions}")
    print(f"Output folder: {out_dir.resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch scrape UPSC PYQs by year range and subject list."
    )
    parser.add_argument("--start-year", type=int, required=True, help="Start year (e.g. 2011)")
    parser.add_argument("--end-year", type=int, required=True, help="End year (e.g. 2025)")
    parser.add_argument(
        "--subjects",
        nargs="+",
        default=["all"],
        help='Subjects to scrape. Use "all" or one/more exact names.',
    )
    parser.add_argument(
        "--output-dir",
        default="output/json",
        help="Output folder path (default: output/json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.start_year > args.end_year:
        raise ValueError("start-year must be <= end-year")

    if len(args.subjects) == 1 and args.subjects[0].lower() == "all":
        subjects = list(SUBJECTS.keys())
    else:
        invalid = [s for s in args.subjects if s not in SUBJECTS]
        if invalid:
            raise ValueError(
                f"Invalid subjects: {invalid}\nAllowed: {list(SUBJECTS.keys())}"
            )
        subjects = args.subjects

    run_batch(
        start_year=args.start_year,
        end_year=args.end_year,
        subjects=subjects,
        out_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()
