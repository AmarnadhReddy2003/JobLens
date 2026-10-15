from collections import Counter

from loader import load_all
from skill_extractor import extract_from_all_jds, SKILL_CATEGORIES


def analyze_skills(extraction_results):
    skill_counts = Counter()
    total_jds = len(extraction_results)

    for jd in extraction_results:
        for skill in set(jd["skills"]):
            skill_counts[skill] += 1

    results = []

    for skill, count in skill_counts.most_common():
        percentage = count / total_jds * 100 if total_jds else 0

        results.append({
            "skill": skill,
            "job_count": count,
            "percentage": round(percentage, 2)
        })

    return results


def analyze_categories(extraction_results):
    category_counts = Counter()
    total_jds = len(extraction_results)

    for jd in extraction_results:
        for category in set(jd["categories"]):
            category_counts[category] += 1

    results = []

    for category, count in category_counts.most_common():
        percentage = count / total_jds * 100 if total_jds else 0

        results.append({
            "category": category,
            "job_count": count,
            "percentage": round(percentage, 2)
        })

    return results


def display_summary(total_jds, skill_analysis):
    print("\nJOBLENS SKILL ANALYSIS")
    print("=" * 65)

    print(f"Job descriptions analyzed: {total_jds}")
    print(f"Unique skills detected: {len(skill_analysis)}")

    print("\nMOST FREQUENT SKILLS")
    print("-" * 65)

    for item in skill_analysis[:5]:
        print(
            f"{item['skill']}: "
            f"{item['job_count']}/{total_jds} jobs "
            f"({item['percentage']:.2f}%)"
        )

    print(
        "\nNote: The five skills above are a quick summary. "
        "All detected skills appear below."
    )


def display_category_summary(category_analysis):
    print("\nCATEGORY SUMMARY")
    print("-" * 65)

    for item in category_analysis:
        print(
            f"{item['category']}: "
            f"{item['job_count']}/{total_jobs} jobs "
            f"({item['percentage']:.2f}%)"
        )


def display_all_skills(extraction_results, skill_analysis):
    print("\nCOMPLETE SKILL ANALYSIS BY CATEGORY")
    print("=" * 65)

    skill_lookup = {
        item["skill"]: item
        for item in skill_analysis
    }

    displayed_skills = set()

    for category, category_skills in SKILL_CATEGORIES.items():
        found_skills = [
            skill for skill in category_skills
            if skill in skill_lookup
        ]

        if not found_skills:
            continue

        print(f"\n{category}")
        print("-" * 65)

        found_skills.sort(
            key=lambda skill: skill_lookup[skill]["job_count"],
            reverse=True
        )

        for skill in found_skills:
            item = skill_lookup[skill]

            print(
                f"  {skill}: "
                f"{item['job_count']}/{len(extraction_results)} jobs "
                f"({item['percentage']:.2f}%)"
            )

            displayed_skills.add(skill)

    # Show any skill that has not been assigned to a category.
    remaining_skills = [
        item for item in skill_analysis
        if item["skill"] not in displayed_skills
    ]

    if remaining_skills:
        print("\nOther Detected Skills")
        print("-" * 65)

        for item in remaining_skills:
            print(
                f"  {item['skill']}: "
                f"{item['job_count']}/{len(extraction_results)} jobs "
                f"({item['percentage']:.2f}%)"
            )


def main():
    global total_jobs

    job_descriptions = load_all()

    if not job_descriptions:
        print("No job descriptions available for analysis.")
        return

    extraction_results = extract_from_all_jds(job_descriptions)

    total_jobs = len(extraction_results)

    skill_analysis = analyze_skills(extraction_results)
    category_analysis = analyze_categories(extraction_results)

    display_summary(total_jobs, skill_analysis)
    display_category_summary(category_analysis)
    display_all_skills(extraction_results, skill_analysis)


if __name__ == "__main__":
    main()