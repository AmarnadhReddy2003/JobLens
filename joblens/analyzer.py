from collections import Counter, defaultdict
from pathlib import Path

from joblens.config import MY_SKILLS_FILE
from joblens.extractor import (
    extract_from_all_jds,
    load_skill_config,
)
from joblens.loader import load_all
from joblens.models import JobDescription


PROFILE_STATUSES = {"know", "used", "learning"}


def load_profile(path: str | Path = MY_SKILLS_FILE) -> dict[str, str]:
    """Load profile skills and optional proficiency labels."""
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Profile skills file not found: {path}")

    skill_dictionary, _ = load_skill_config()

    # Map standard names and aliases to canonical skill names.
    aliases = {}
    for skill, skill_aliases in skill_dictionary.items():
        aliases[skill.casefold()] = skill

        for alias in skill_aliases:
            aliases[alias.casefold()] = skill

    profile = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        # Supports plain names and formats such as "Python | know".
        parts = line.split("|", maxsplit=1)
        skill_text = parts[0].strip()
        status = parts[1].strip().casefold() if len(parts) == 2 else "unspecified"

        # Also accept "Python: know".
        if status == "unspecified" and ":" in skill_text:
            possible_skill, possible_status = skill_text.rsplit(":", 1)
            if possible_status.strip().casefold() in PROFILE_STATUSES:
                skill_text = possible_skill.strip()
                status = possible_status.strip().casefold()

        canonical = aliases.get(skill_text.casefold())

        if canonical:
            if status not in PROFILE_STATUSES:
                status = "unspecified"
            profile[canonical] = status

    return profile


def analyze_jobs(
    jobs: list[JobDescription],
    profile_path: str | Path = MY_SKILLS_FILE,
) -> dict:
    """Calculate skill frequency, category frequency and profile comparisons."""
    skill_dictionary, skill_categories = load_skill_config()
    profile = load_profile(profile_path)

    extracted = extract_from_all_jds(jobs)
    total_jobs = len(extracted)

    skill_counts = Counter()
    category_job_counts = Counter()
    per_job = []

    for job_result in extracted:
        skills = set(job_result["skills"])

        # Count a skill no more than once per posting.
        skill_counts.update(skills)

        # Count each category at most once per posting.
        for category, category_skills in skill_categories.items():
            if skills.intersection(category_skills):
                category_job_counts[category] += 1

        per_job.append({
            "file": job_result["file"],
            "company": job_result["company"],
            "title": job_result["title"],
            "skills": sorted(skills),
            "skill_count": len(skills),
        })

    skill_frequency = [
        {
            "skill": skill,
            "jobs": count,
            "percentage": round(count / total_jobs * 100, 2)
            if total_jobs else 0.0,
        }
        for skill, count in skill_counts.most_common()
    ]

    category_frequency = [
        {
            "category": category,
            "jobs": count,
            "percentage": round(count / total_jobs * 100, 2)
            if total_jobs else 0.0,
        }
        for category, count in category_job_counts.most_common()
    ]

    detected_skills = set(skill_counts)
    profile_matches = sorted(detected_skills.intersection(profile))
    skills_to_review = sorted(detected_skills.difference(profile))

    return {
        "summary": {
            "jobs_analyzed": total_jobs,
            "unique_skills": len(detected_skills),
            "profile_matches": len(profile_matches),
            "skills_to_review": len(skills_to_review),
        },
        "skill_frequency": skill_frequency,
        "category_frequency": category_frequency,
        "profile_matches": [
            {"skill": skill, "status": profile[skill]}
            for skill in profile_matches
        ],
        # These skills need review; this does not mean the user lacks them.
        "skills_to_review": skills_to_review,
        "per_job": per_job,
    }


def main() -> None:
    """Print a short summary; keep detailed results available to callers."""
    load_result = load_all()

    if load_result.failures:
        print(f"Warning: {len(load_result.failures)} job file(s) could not be loaded.")

    if not load_result.jobs:
        print("JOBLENS — ANALYSIS")
        print("No job descriptions available.")
        return

    try:
        report = analyze_jobs(load_result.jobs)
    except (OSError, ValueError) as error:
        print(f"Analysis failed: {error}")
        return

    summary = report["summary"]
    top_skill = (
        report["skill_frequency"][0]
        if report["skill_frequency"] else None
    )

    print("JOBLENS — ANALYSIS COMPLETE")
    print(f"Jobs analyzed: {summary['jobs_analyzed']}")
    print(f"Unique skills found: {summary['unique_skills']}")

    if top_skill:
        print(
            f"Most requested skill: {top_skill['skill']} "
            f"({top_skill['jobs']}/{summary['jobs_analyzed']} jobs)"
        )

    print(f"Profile matches: {summary['profile_matches']}")
    print(f"Skills to review: {summary['skills_to_review']}")
    print("Detailed results are available from analyze_jobs().")


if __name__ == "__main__":
    main()