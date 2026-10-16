import json
import re
from pathlib import Path

from joblens.config import DATA_DIR
from joblens.models import JobDescription


SKILLS_FILE = DATA_DIR / "skills.json"


def load_skill_config(
    path: str | Path = SKILLS_FILE,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Load skill aliases and categories from the JSON configuration."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    skills = config.get("skills")
    categories = config.get("categories")

    if not isinstance(skills, dict) or not isinstance(categories, dict):
        raise ValueError(
            "skills.json must contain 'skills' and 'categories' objects."
        )

    for skill, aliases in skills.items():
        if not isinstance(skill, str) or not isinstance(aliases, list):
            raise ValueError(f"Invalid skill entry: {skill!r}")

        if not all(isinstance(alias, str) and alias.strip() for alias in aliases):
            raise ValueError(f"Invalid aliases for skill: {skill}")

    known_skills = set(skills)

    for category, category_skills in categories.items():
        if not isinstance(category, str) or not isinstance(category_skills, list):
            raise ValueError(f"Invalid category entry: {category!r}")

        unknown = set(category_skills) - known_skills
        if unknown:
            raise ValueError(
                f"Category {category!r} contains unknown skills: "
                f"{sorted(unknown)}"
            )

    return skills, categories


def contains_skill(text: str, alias: str) -> bool:
    """Match a complete alias without matching it inside larger words."""
    pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None

def extract_skills(
    text: str,
    skill_dictionary: dict[str, list[str]] | None = None,
) -> list[str]:
    """Return each detected standard skill at most once."""
    if skill_dictionary is None:
        skill_dictionary, _ = load_skill_config()

    found_skills = []

    for skill, aliases in skill_dictionary.items():
        if any(contains_skill(text, alias) for alias in aliases):
            found_skills.append(skill)

    # Avoid detecting Java from the "java script" alias of JavaScript.
    if "JavaScript" in found_skills and re.search(
        r"(?<!\w)java\s+script(?!\w)",
        text,
        flags=re.IGNORECASE,
    ):
        found_skills = [
            skill for skill in found_skills
            if skill != "Java"
        ]

    return found_skills

def categorize_skills(
    skills: list[str],
    skill_categories: dict[str, list[str]] | None = None,
) -> dict[str, list[str]]:
    """Group detected skills using the configured categories."""
    if skill_categories is None:
        _, skill_categories = load_skill_config()

    skill_set = set(skills)
    categorized = {}

    for category, category_skills in skill_categories.items():
        matched = [
            skill for skill in category_skills
            if skill in skill_set
        ]

        if matched:
            categorized[category] = matched

    return categorized


def extract_from_all_jds(
    job_descriptions: list[JobDescription],
) -> list[dict]:
    """Extract skills and categories from loaded job descriptions."""
    skill_dictionary, skill_categories = load_skill_config()
    results = []

    for job in job_descriptions:
        skills = extract_skills(job.body, skill_dictionary)

        results.append({
            "file": job.file,
            "company": job.company or "Unknown",
            "title": job.title or "Unknown",
            "skills": skills,
            "categories": categorize_skills(
                skills,
                skill_categories,
            ),
        })

    return results


if __name__ == "__main__":
    from joblens.loader import load_all

    load_result = load_all()
    results = extract_from_all_jds(load_result.jobs)

    print("JOBLENS V2 — SKILL EXTRACTION")
    print(f"Processed: {len(results)} | Load failures: {len(load_result.failures)}")

    for result in results:
        print(
            f"{result['file']} | {result['company']} | "
            f"{result['title']} | Skills: {len(result['skills'])}"
        )

    for failure in load_result.failures:
        print(f"LOAD ERROR: {failure}")