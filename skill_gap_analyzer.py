
from pathlib import Path

from loader import load_all
from skill_extractor import extract_from_all_jds, extract_skills


def load_my_skills(path="my_skills.txt"):
    skills_file = Path(path)

    if not skills_file.exists():
        raise FileNotFoundError(
            f"{path} not found. Create the file and list your skills."
        )

    with open(skills_file, "r", encoding="utf-8") as file:
        text = file.read()

    # Use the same dictionary as the job description extractor.
    return set(extract_skills(text))


def analyze_skill_gaps(extraction_results, my_skills):
    required_skill_counts = {}

    for jd in extraction_results:
        # Count each skill at most once per job description.
        unique_skills = set(jd["skills"])

        for skill in unique_skills:
            required_skill_counts[skill] = (
                required_skill_counts.get(skill, 0) + 1
            )

    # Skills found in job descriptions but not in your profile.
    missing_skills = []

    # Skills found in both job descriptions and your profile.
    matched_skills = []

    for skill, count in required_skill_counts.items():
        percentage = (
            count / len(extraction_results) * 100
            if extraction_results
            else 0
        )

        result = {
            "skill": skill,
            "job_count": count,
            "percentage": round(percentage, 2)
        }

        if skill in my_skills:
            matched_skills.append(result)
        else:
            missing_skills.append(result)

    matched_skills.sort(
        key=lambda item: item["job_count"],
        reverse=True
    )

    missing_skills.sort(
        key=lambda item: item["job_count"],
        reverse=True
    )

    return matched_skills, missing_skills


def display_results(matched_skills, missing_skills, total_jds):
    print("\nJOBLENS SKILL-GAP ANALYSIS")
    print("=" * 65)
    print("Job descriptions analyzed:", total_jds)

    print("\nSKILLS MATCHING YOUR PROFILE")
    print("-" * 65)

    if matched_skills:
        for item in matched_skills:
            print(
                f"{item['skill']:<30} "
                f"{item['job_count']} jobs "
                f"({item['percentage']:.2f}%)"
            )
    else:
        print("No matching skills found.")

    print("\nSKILLS TO REVIEW OR LEARN")
    print("-" * 65)

    if missing_skills:
        for item in missing_skills:
            print(
                f"{item['skill']:<30} "
                f"{item['job_count']} jobs "
                f"({item['percentage']:.2f}%)"
            )
    else:
        print("No skill gaps detected.")

    print("\nSUMMARY")
    print("-" * 65)
    print("Matched skills:", len(matched_skills))
    print("Skills to review or learn:", len(missing_skills))


def main():
    job_descriptions = load_all(".")
    extraction_results = extract_from_all_jds(job_descriptions)

    try:
        my_skills = load_my_skills()
    except (OSError, ValueError) as error:
        print("Could not load your skills:", error)
        return

    total_jds = len(extraction_results)

    if total_jds == 0:
        print("No job descriptions available for analysis.")
        return

    matched_skills, missing_skills = analyze_skill_gaps(
        extraction_results,
        my_skills
    )

    display_results(
        matched_skills,
        missing_skills,
        total_jds
    )


if __name__ == "__main__":
    main()
