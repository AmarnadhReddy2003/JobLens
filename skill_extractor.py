import re

from loader import load_all


# Standard skill names and their accepted aliases
SKILL_DICTIONARY = {
    # Programming languages
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "java script"],
    "C": ["c language"],
    "C++": ["c++"],
    "C#": ["c#"],
    "SQL": ["sql"],
    "TypeScript": ["typescript"],

    # Web development
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi", "fast api"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs"],
    "HTML": ["html"],
    "CSS": ["css"],
    "Angular": ["angular", "angularjs"],
    "REST APIs": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis"
    ],

    # Databases
    "Database Management": [
        "database management",
        "database administration"
    ],
    "MongoDB": ["mongodb", "mongo db"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "Oracle": ["oracle"],

    # AI and machine learning
    "Machine Learning": ["machine learning"],
    "Deep Learning": ["deep learning"],
    "Generative AI": ["generative ai", "genai", "gen ai"],
    "NLP": ["natural language processing", "nlp"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],

    # Development tools and practices
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes"],
    "CI/CD": [
        "ci/cd",
        "continuous integration",
        "continuous deployment"
    ],
    "Selenium": ["selenium"],
    "Robot Framework": ["robot framework"],
    "Agile": ["agile"],
    "Jira": ["jira"],
    "Unit Testing": ["unit testing", "unit tests"],
    "API Testing": ["api testing"],
    "Software Testing": ["software testing"],
    "Debugging": ["debugging"],
    "Version Control": ["version control"],

    # Computer science fundamentals
    "OOP": [
        "object-oriented programming",
        "object oriented programming",
        "oop"
    ],
    "DSA": [
        "data structures and algorithms",
        "data structures",
        "dsa"
    ],

    # Software engineering concepts
    "Software Engineering": ["software engineering"],
    "Software Development": [
        "software development",
        "application development"
    ],
    "Software Design": ["software design"],
    "Software Maintenance": [
        "software maintenance",
        "application maintenance"
    ],
    "Programming Concepts": [
        "programming concepts",
        "software development fundamentals"
    ],
    "Problem Solving": [
        "problem-solving",
        "problem solving"
    ],
    "Performance Optimization": [
        "performance optimization",
        "optimization of software",
        "performance analysis"
    ],
    "Technical Support": ["technical support"],
    "Data Analysis": ["data analysis"],
    "Troubleshooting": [
        "troubleshooting",
        "troubleshoot"
    ],
    "Code Review": [
        "code review",
        "code reviews"
    ],
    "Communication": [
        "communication",
        "communication skills"
    ],
    "Teamwork": [
        "teamwork",
        "team work"
    ],
}


# Group skills into categories for later analysis
SKILL_CATEGORIES = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "C", "C++", "C#",
        "TypeScript"
    ],
    "Databases and Query Languages": [
        "SQL", "Database Management", "MongoDB",
        "PostgreSQL", "MySQL", "Oracle"
    ],
    "Web Technologies and Frameworks": [
        "Django", "Flask", "FastAPI", "React", "Node.js",
        "HTML", "CSS", "Angular", "REST APIs"
    ],
    "AI and Machine Learning": [
        "Machine Learning", "Deep Learning", "Generative AI",
        "NLP", "TensorFlow", "PyTorch", "scikit-learn"
    ],
    "Development Tools and Testing": [
        "Git", "GitHub", "Docker", "Kubernetes", "CI/CD",
        "Selenium", "Robot Framework", "Jira",
        "Unit Testing", "API Testing", "Software Testing",
        "Version Control"
    ],
    "Computer Science Fundamentals": [
        "OOP", "DSA", "Programming Concepts"
    ],
    "Software Engineering Concepts": [
        "Software Engineering", "Software Development",
        "Software Design", "Software Maintenance",
        "Problem Solving", "Debugging",
        "Performance Optimization", "Troubleshooting",
        "Code Review"
    ],
    "Other Skills": [
        "Agile", "Technical Support", "Data Analysis",
        "Communication", "Teamwork"
    ],
}


def contains_skill(text, alias):
    # Match the complete phrase, ignoring capitalization.
    pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE
    ) is not None


def extract_skills(text):
    found_skills = []

    for skill, aliases in SKILL_DICTIONARY.items():
        for alias in aliases:
            if contains_skill(text, alias):
                found_skills.append(skill)
                break

    return found_skills


def categorize_skills(skills):
    categorized = {}

    for category, category_skills in SKILL_CATEGORIES.items():
        matched = [
            skill for skill in skills
            if skill in category_skills
        ]

        if matched:
            categorized[category] = matched

    return categorized


def extract_from_all_jds(job_descriptions):
    results = []

    for jd in job_descriptions:
        meta = jd["meta"]
        body = jd["body"]

        skills = extract_skills(body)

        results.append({
            "file": jd["file"],
            "company": meta.get("COMPANY", "Unknown"),
            "title": meta.get("TITLE", "Unknown"),
            "skills": skills,
            "categories": categorize_skills(skills)
        })

    return results


if __name__ == "__main__":
    job_descriptions = load_all(".")
    results = extract_from_all_jds(job_descriptions)

    print("\nJOBLENS SKILL EXTRACTION")
    print("------------------------")
    print("Total JDs processed:", len(results))

    for jd in results:
        print(f"\nFile: {jd['file']}")
        print(f"Company: {jd['company']}")
        print(f"Title: {jd['title']}")

        if jd["skills"]:
            print("Skills found:", ", ".join(jd["skills"]))

            for category, skills in jd["categories"].items():
                print(f"  {category}: {', '.join(skills)}")
        else:
            print("Skills found: None")