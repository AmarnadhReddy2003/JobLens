
import json
import re
from pathlib import Path

from joblens.config import DATA_DIR
from joblens.models import JobDescription


SKILLS_FILE = DATA_DIR / "skills.json"


def load_skill_config(
    path: str | Path = SKILLS_FILE,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Load and validate skill aliases and categories."""
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

        if not all(
            isinstance(alias, str) and alias.strip()
            for alias in aliases
        ):
            raise ValueError(f"Invalid aliases for skill: {skill}")

    known_skills = set(skills)

    for category, category_skills in categories.items():
        if not isinstance(category, str) or not isinstance(
            category_skills, list
        ):
            raise ValueError(f"Invalid category entry: {category!r}")

        unknown = set(category_skills) - known_skills
        if unknown:
            raise ValueError(
                f"Category {category!r} contains unknown skills: "
                f"{sorted(unknown)}"
            )

    return skills, categories


def contains_skill(text: str, alias: str) -> bool:
    """Match a complete alias without matching inside larger words."""
    pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_skills(
    text: str,
    skill_dictionary: dict[str, list[str]] | None = None,
) -> list[str]:
    """Extract canonical skill names without duplicates."""
    if skill_dictionary is None:
        skill_dictionary, _ = load_skill_config()

    found_skills = []

    for skill, aliases in skill_dictionary.items():
        if any(contains_skill(text, alias) for alias in aliases):
            found_skills.append(skill)

    # Prevent Java from being detected from the "Java script" alias.
    if "JavaScript" in found_skills and re.search(
        r"(?<!\w)java\s*script(?!\w)",
        text,
        flags=re.IGNORECASE,
    ):
        found_skills = [
            skill for skill in found_skills
            if skill != "Java"
        ]

    return found_skills


def _split_sentences(text: str) -> list[str]:
    """Split text at common sentence-ending punctuation."""
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if sentence.strip()
    ]


def _classify_sentence(
    sentence: str,
    aliases: list[str],
) -> str:
    """Classify a skill mention within one sentence."""
    matching_aliases = [
        alias for alias in aliases
        if contains_skill(sentence, alias)
    ]

    if not matching_aliases:
        return "not_mentioned"

    statuses = []

    for alias in matching_aliases:
        skill_pattern = (
            r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
        )

        patterns = {
            "not_required": (
                skill_pattern
                + r"(?:\s+\w+){0,4}\s+"
                + r"(?:is\s+)?not\s+required\b"
            ),
            # Handles phrases such as "Python is not required"
            # separately from a simple "not Python" construction.
            "negated_prefix": (
                r"\bnot\s+" + skill_pattern
            ),
            "negated": (
                skill_pattern
                + r"(?:\s+\w+){0,3}\s+"
                + r"(?:is\s+)?(?:not\s+used|not\s+utilized"
                + r"|unavailable)\b"
            ),
            "negated_action": (
                r"\b(?:do not|don't|does not|doesn't|did not|"
                r"didn't|never use)\b"
                + r"(?:\s+\w+){0,4}\s+"
                + skill_pattern
            ),
            "preferred": (
                skill_pattern
                + r"(?:\s+\w+){0,3}\s+"
                + r"(?:is\s+)?(?:preferred|a plus)\b"
            ),
            "required": (
                skill_pattern
                + r"(?:\s+\w+){0,3}\s+"
                + r"(?:is\s+)?required\b"
            ),
        }

        status = "mentioned"

        for candidate in (
            "not_required",
            "negated_prefix",
            "negated",
            "negated_action",
            "preferred",
            "required",
        ):
            if re.search(
                patterns[candidate],
                sentence,
                flags=re.IGNORECASE,
            ):
                # Normalize negation rules to one public status.
                if candidate in ("negated_prefix", "negated_action"):
                    status = "negated"
                else:
                    status = candidate
                break

        statuses.append(status)

    substantive_statuses = set(statuses) - {"mentioned"}

    if not substantive_statuses:
        return "mentioned"

    if len(substantive_statuses) == 1:
        return substantive_statuses.pop()

    return "mixed"


def classify_skill_context(
    text: str,
    skill: str,
    aliases: list[str] | None = None,
) -> str:
    """
    Classify skill context using lines and individual sentences.

    Possible results:
    required, preferred, not_required, negated,
    mentioned, not_mentioned, mixed.
    """
    skill_aliases = list(dict.fromkeys(aliases or [skill]))

    if skill not in skill_aliases:
        skill_aliases.insert(0, skill)

    line_statuses = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        matching_aliases = [
            alias for alias in skill_aliases
            if contains_skill(line, alias)
        ]

        if not matching_aliases:
            continue

        # Classify headings that apply to a semicolon-separated list.
        if re.search(
            r"\b(?:preferred(?:\s+but\s+not\s+essential)?"
            r"|desirable|nice\s+to\s+have)\s*:",
            line,
            flags=re.IGNORECASE,
        ):
            line_statuses.append("preferred")
            continue

        if re.search(
            r"\b(?:required|mandatory)\s*:",
            line,
            flags=re.IGNORECASE,
        ):
            line_statuses.append("required")
            continue

        # Otherwise, classify the skill's context sentence by sentence.
        for sentence in _split_sentences(line):
            status = _classify_sentence(sentence, skill_aliases)

            if status != "not_mentioned":
                line_statuses.append(status)

    if not line_statuses:
        return "not_mentioned"

    explicit_statuses = set(line_statuses) - {"mentioned"}

    if not explicit_statuses:
        return "mentioned"

    if len(explicit_statuses) > 1:
        return "mixed"

    return explicit_statuses.pop()


def categorize_skills(
    skills: list[str],
    skill_categories: dict[str, list[str]] | None = None,
) -> dict[str, list[str]]:
    """Group detected skills into configured categories."""
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
    """Extract skills, categories, and contexts for each job."""
    skill_dictionary, skill_categories = load_skill_config()
    results = []

    for job in job_descriptions:
        skills = extract_skills(job.body, skill_dictionary)

        skill_contexts = {
            skill: classify_skill_context(
                job.body,
                skill,
                aliases=skill_dictionary.get(skill, [skill]),
            )
            for skill in skills
        }

        results.append({
            "file": job.file,
            "company": job.company or "Unknown",
            "title": job.title or "Unknown",
            "skills": skills,
            "categories": categorize_skills(
                skills,
                skill_categories,
            ),
            "skill_contexts": skill_contexts,
        })

    return results


if __name__ == "__main__":
    from joblens.loader import load_all

    load_result = load_all()
    results = extract_from_all_jds(load_result.jobs)

    print("JOBLENS V2 - SKILL EXTRACTION")
    print(
        f"Processed: {len(results)} | "
        f"Load failures: {len(load_result.failures)}"
    )

    for result in results:
        print(
            f"{result['file']} | {result['company']} | "
            f"{result['title']} | Skills: {len(result['skills'])}"
        )
        print(f"  Contexts: {result['skill_contexts']}")

    for failure in load_result.failures:
        print(f"LOAD ERROR: {failure}")
