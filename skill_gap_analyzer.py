from pathlib import Path

from loader import load_all
from skill_extractor import (
    extract_from_all_jds,
    extract_skills,
    SKILL_CATEGORIES
)


def load_my_skills(path="my_skills.txt"):
    skills_file = Path(path)

    if not skills_file.exists():
        raise FileNotFoundError(
            f"{path} not found. Create the file and list your skills."
        )

    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    return set(extract_skills(text))


def analyze_skill_gaps(extraction_results, my_skills):
    required_skill_counts = {}

    for jd in extraction_results:
        for skill in set(jd["skills"]):
            required_skill_counts[skill] = (
                required_skill_counts.get(skill, 0) + 1
            )

    total_jds = len(extraction_results)
    matched_skills = []
    review_skills = []

    for skill, count in required_skill_counts.items():
        percentage = count / total_jds * 100 if total_jds else 0

        result = {
            "skill": skill,
            "job_count": count,
            "percentage": round(percentage, 2),
            "status": (
                "Matched" if skill in my_skills
                else "Review or learn"
            )
        }

        if skill in my_skills:
            matched_skills.append(result)
        else:
            review_skills.append(result)

    matched_skills.sort(
        key=lambda item: item["job_count"],
        reverse=True
    )

    review_skills.sort(
        key=lambda item: item["job_count"],
        reverse=True
    )

    return matched_skills, review_skills


def display_skill_group(title, skills, total_jds):
    print(f"\n{title}")
    print("-" * 65)

    if not skills:
        print("No skills in this group.")
        return

    skill_lookup = {
        item["skill"]: item
        for item in skills
    }

    displayed_skills = set()

    for category, category_skills in SKILL_CATEGORIES.items():
        found_skills = [
            skill for skill in category_skills
            if skill in skill_lookup
        ]

        if not found_skills:
            continue

        print(f"\n{category}:")

        found_skills.sort(
            key=lambda skill: skill_lookup[skill]["job_count"],
            reverse=True
        )

        for skill in found_skills:
            item = skill_lookup[skill]

            print(
                f"  {skill}: "
                f"{item['job_count']}/{total_jds} jobs "
                f"({item['percentage']:.2f}%)"
            )

            displayed_skills.add(skill)

    remaining = [
        item for item in skills
        if item["skill"] not in displayed_skills
    ]

    if remaining:
        print("\nOther Skills:")

        for item in remaining:
            print(
                f"  {item['skill']}: "
                f"{item['job_count']}/{total_jds} jobs "
                f"({item['percentage']:.2f}%)"
            )


def main():
    job_descriptions = load_all()

    if not job_descriptions:
        print("No job descriptions available for analysis.")
        return

    extraction_results = extract_from_all_jds(job_descriptions)

    try:
        my_skills = load_my_skills()
    except (OSError, ValueError) as error:
        print("Could not load your skills:", error)
        return

    total_jds = len(extraction_results)

    matched_skills, review_skills = analyze_skill_gaps(
        extraction_results,
        my_skills
    )

    print("\nJOBLENS SKILL-GAP ANALYSIS")
    print("=" * 65)

    print(f"Job descriptions analyzed: {total_jds}")
    print(f"Confirmed profile matches: {len(matched_skills)}")
    print(f"Skills to review: {len(review_skills)}")

    display_skill_group(
        "SKILLS MATCHING YOUR PROFILE",
        matched_skills,
        total_jds
    )

    display_skill_group(
        "SKILLS TO REVIEW OR LEARN",
        review_skills,
        total_jds
    )

    print("\nINTERPRETATION")
    print("-" * 65)
    print(
        "A skill listed for review is not confirmed in your profile. "
        "It does not necessarily mean you lack that skill."
    )
    print(
        "Frequency shows how often a skill appeared in the collected "
        "job descriptions. It does not independently determine "
        "whether a skill is essential for a particular role."
    )


if __name__ == "__main__":
    main()