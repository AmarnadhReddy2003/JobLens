
import csv
import json
from collections import Counter
from pathlib import Path

from loader import load_all
from skill_extractor import extract_from_all_jds
from skill_gap_analyzer import load_my_skills


OUTPUT_DIR = Path("reports")


def calculate_skill_frequency(extraction_results):
    counts = Counter()
    total_jds = len(extraction_results)

    for jd in extraction_results:
        for skill in set(jd["skills"]):
            counts[skill] += 1

    results = []

    for skill, count in counts.most_common():
        results.append({
            "skill": skill,
            "job_count": count,
            "percentage": round(
                count / total_jds * 100, 2
            ) if total_jds else 0
        })

    return results


def calculate_category_frequency(extraction_results):
    counts = Counter()
    total_jds = len(extraction_results)

    for jd in extraction_results:
        for category in set(jd["categories"]):
            counts[category] += 1

    results = []

    for category, count in counts.most_common():
        results.append({
            "category": category,
            "job_count": count,
            "percentage": round(
                count / total_jds * 100, 2
            ) if total_jds else 0
        })

    return results


def calculate_skill_gaps(extraction_results, my_skills):
    counts = Counter()
    total_jds = len(extraction_results)

    for jd in extraction_results:
        for skill in set(jd["skills"]):
            counts[skill] += 1

    results = []

    for skill, count in counts.most_common():
        results.append({
            "skill": skill,
            "job_count": count,
            "percentage": round(
                count / total_jds * 100, 2
            ) if total_jds else 0,
            "status": (
                "Matched"
                if skill in my_skills
                else "Review or learn"
            )
        })

    return results


def write_csv(filename, rows, fieldnames):
    path = OUTPUT_DIR / filename

    with open(path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {path}")


def write_json(filename, data):
    path = OUTPUT_DIR / filename

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Created: {path}")


def write_text_report(
    filename,
    total_jds,
    skill_frequency,
    category_frequency,
    skill_gaps
):
    path = OUTPUT_DIR / filename

    matched = [
        item for item in skill_gaps
        if item["status"] == "Matched"
    ]

    missing = [
        item for item in skill_gaps
        if item["status"] == "Review or learn"
    ]

    with open(path, "w", encoding="utf-8") as file:
        file.write("JOBLENS PROJECT REPORT\n")
        file.write("=" * 50 + "\n\n")

        file.write(f"Job descriptions analyzed: {total_jds}\n")
        file.write(f"Matched skills: {len(matched)}\n")
        file.write(f"Skills to review or learn: {len(missing)}\n\n")

        file.write("TOP SKILLS\n")
        file.write("-" * 50 + "\n")

        for item in skill_frequency[:10]:
            file.write(
                f"{item['skill']}: {item['job_count']} jobs "
                f"({item['percentage']:.2f}%)\n"
            )

        file.write("\nCATEGORY FREQUENCY\n")
        file.write("-" * 50 + "\n")

        for item in category_frequency:
            file.write(
                f"{item['category']}: {item['job_count']} jobs "
                f"({item['percentage']:.2f}%)\n"
            )

        file.write("\nSKILLS TO REVIEW OR LEARN\n")
        file.write("-" * 50 + "\n")

        for item in missing:
            file.write(
                f"{item['skill']}: {item['job_count']} jobs "
                f"({item['percentage']:.2f}%)\n"
            )

        file.write(
            "\nInterpretation: Results describe only the collected "
            "job descriptions. A skill marked 'Review or learn' is "
            "absent from the supplied skill profile; it does not "
            "prove the person lacks that skill.\n"
        )

    print(f"Created: {path}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    job_descriptions = load_all()
    total_jds = len(job_descriptions)

    if total_jds == 0:
        print("No job descriptions found. Nothing to export.")
        return

    try:
        my_skills = load_my_skills()
    except (OSError, ValueError) as error:
        print("Could not load my_skills.txt:", error)
        return

    extraction_results = extract_from_all_jds(job_descriptions)

    skill_frequency = calculate_skill_frequency(
        extraction_results
    )

    category_frequency = calculate_category_frequency(
        extraction_results
    )

    skill_gaps = calculate_skill_gaps(
        extraction_results,
        my_skills
    )

    # Export individual skill frequency
    write_csv(
        "skill_frequency.csv",
        skill_frequency,
        ["skill", "job_count", "percentage"]
    )

    # Export category frequency
    write_csv(
        "category_frequency.csv",
        category_frequency,
        ["category", "job_count", "percentage"]
    )

    # Export skill-gap results
    write_csv(
        "skill_gap_report.csv",
        skill_gaps,
        ["skill", "job_count", "percentage", "status"]
    )

    # Export a combined JSON report
    report_data = {
        "project": "JobLens",
        "total_job_descriptions": total_jds,
        "skill_frequency": skill_frequency,
        "category_frequency": category_frequency,
        "skill_gap_analysis": {
            "matched_skills": [
                item for item in skill_gaps
                if item["status"] == "Matched"
            ],
            "skills_to_review_or_learn": [
                item for item in skill_gaps
                if item["status"] == "Review or learn"
            ]
        }
    }

    write_json("skill_gap_report.json", report_data)

    # Export a readable summary
    write_text_report(
        "joblens_report.txt",
        total_jds,
        skill_frequency,
        category_frequency,
        skill_gaps
    )

    print("\nJOBLENS REPORT GENERATION COMPLETE")
    print("----------------------------------")
    print("Job descriptions analyzed:", total_jds)
    print("Output folder:", OUTPUT_DIR.resolve())


if __name__ == "__main__":
    main()
