
from collections import Counter

from loader import load_all
from skill_extractor import extract_from_all_jds


def analyze_skills(extraction_results):
    skill_counts = Counter()
    total_jds = len(extraction_results)

    for jd in extraction_results:
        # Count each skill only once per job description.
        unique_skills = set(jd["skills"])

        for skill in unique_skills:
            skill_counts[skill] += 1

    skill_analysis = []

#  Percentage = (Jobs containing the skill or category/(Total jobs analyzed))*100

    for skill, count in skill_counts.most_common():
        percentage = (
            count / total_jds * 100
            if total_jds > 0
            else 0
        )

        skill_analysis.append({
            "skill": skill,
            "job_count": count,
            "percentage": round(percentage, 2)
        })

    return skill_analysis


def analyze_categories(extraction_results):
    category_counts = Counter()
    total_jds = len(extraction_results)

    for jd in extraction_results:
        # Count a category at most once per job description.
        # Multiple skills from the same category count as one job.
        categories_found = set(jd["categories"].keys())

        for category in categories_found:
            category_counts[category] += 1

    category_analysis = []

    for category, count in category_counts.most_common():
        percentage = (
            count / total_jds * 100
            if total_jds > 0
            else 0
        )

        category_analysis.append({
            "category": category,
            "job_count": count,
            "percentage": round(percentage, 2)
        })

    return category_analysis


def display_skill_analysis(skill_analysis, total_jds):
    print("\nINDIVIDUAL SKILL FREQUENCY")
    print("-" * 65)
    print(f"{'Skill':<30} {'Job Count':<12} {'Percentage':<12}")
    print("-" * 65)

    if not skill_analysis:
        print("No skills found.")
        return

    for item in skill_analysis:
        print(
            f"{item['skill']:<30} "
            f"{item['job_count']:<12} "
            f"{item['percentage']:.2f}%"
        )


def display_category_analysis(category_analysis):
    print("\nCATEGORY FREQUENCY")
    print("-" * 75)
    print(f"{'Category':<40} {'Job Count':<12} {'Percentage':<12}")
    print("-" * 75)

    if not category_analysis:
        print("No categories found.")
        return

    for item in category_analysis:
        print(
            f"{item['category']:<40} "
            f"{item['job_count']:<12} "
            f"{item['percentage']:.2f}%"
        )


def main():
    job_descriptions = load_all(".")

    # Extract skills and categories from all loaded descriptions.
    extraction_results = extract_from_all_jds(job_descriptions)

    total_jds = len(extraction_results)

    print("\nJOBLENS SKILL ANALYSIS")
    print("=" * 65)
    print("Total job descriptions analyzed:", total_jds)

    if total_jds == 0:
        print("No job descriptions available for analysis.")
        return

    skill_analysis = analyze_skills(extraction_results)
    category_analysis = analyze_categories(extraction_results)

    display_skill_analysis(skill_analysis, total_jds)
    display_category_analysis(category_analysis)


if __name__ == "__main__":
    main()
