
import csv
import json

from joblens.config import REPORTS_DIR
from joblens.analyzer import analyze_jobs
from joblens.loader import load_all


def write_csv(path, fieldnames, rows):
    """Write rows of data to a CSV file."""
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_reports():
    """Analyze job descriptions and save all reports."""
    output_dir = REPORTS_DIR / "v2"
    output_dir.mkdir(parents=True, exist_ok=True)

    load_result = load_all()
    analysis = analyze_jobs(load_result.jobs)

    # Report 1: Skill frequency
    write_csv(
        output_dir / "skill_frequency.csv",
        ["skill", "jobs", "percentage"],
        analysis["skill_frequency"],
    )

    # Report 2: Category frequency
    write_csv(
        output_dir / "category_frequency.csv",
        ["category", "jobs", "percentage"],
        analysis["category_frequency"],
    )

    # Prepare profile matches and skills to review.
    frequency = {
        item["skill"]: item
        for item in analysis["skill_frequency"]
    }

    profile_status = {
        item["skill"]: item["status"]
        for item in analysis["profile_matches"]
    }

    gap_rows = []

    for skill, status in profile_status.items():
        item = frequency[skill]

        gap_rows.append({
            "skill": skill,
            "jobs": item["jobs"],
            "percentage": item["percentage"],
            "profile_status": status,
            "classification": "Profile match",
        })

    for skill in analysis["skills_to_review"]:
        item = frequency[skill]

        gap_rows.append({
            "skill": skill,
            "jobs": item["jobs"],
            "percentage": item["percentage"],
            "profile_status": "Not listed",
            "classification": "To review",
        })

    gap_rows.sort(
        key=lambda row: (
            -row["jobs"],
            row["skill"].casefold(),
        )
    )

    # Report 3: Profile matches and skills to review
    write_csv(
        output_dir / "skill_gap_report.csv",
        [
            "skill",
            "jobs",
            "percentage",
            "profile_status",
            "classification",
        ],
        gap_rows,
    )

    # Report 4: Skill context frequency
    write_csv(
        output_dir / "skill_context_frequency.csv",
        ["skill", "context", "jobs", "percentage"],
        analysis["context_frequency"],
    )

    # Report 5: Complete analysis in JSON format
    json_report = {
        **analysis,
        "load_failures": load_result.failures,
    }

    with (output_dir / "skill_gap_report.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(json_report, file, indent=2, ensure_ascii=False)

    print("JOBLENS V2 - REPORTS GENERATED")
    print(f"Jobs analyzed: {analysis['summary']['jobs_analyzed']}")
    print(f"Reports saved: {output_dir}")
    print("Files created: 5")


if __name__ == "__main__":
    generate_reports()
