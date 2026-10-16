
from joblens.extractor import extract_from_all_jds
from joblens.models import JobDescription
from joblens.extractor import (
    categorize_skills,
    classify_skill_context,
    contains_skill,
    extract_skills,
    load_skill_config,
)


def test_skill_config_loads():
    skills, categories = load_skill_config()

    assert len(skills) == 58
    assert len(categories) == 8


def test_python_is_detected_case_insensitively():
    assert extract_skills("Experience with PYTHON") == ["Python"]


def test_skill_is_detected_only_once():
    result = extract_skills("Python and PYTHON development")

    assert result.count("Python") == 1


def test_c_does_not_match_communication():
    assert contains_skill("communication skills", "c") is False


def test_java_does_not_match_javascript():
    assert contains_skill("JavaScript developer", "java") is False


def test_java_script_alias_does_not_also_match_java():
    result = extract_skills("Build a JAVA SCRIPT application")

    assert "JavaScript" in result
    assert "Java" not in result


def test_cplusplus_is_detected():
    assert "C++" in extract_skills("Experience with C++")


def test_aliases_map_to_standard_skill_names():
    result = extract_skills("Built APIs using RESTful APIs and Fast API")

    assert "REST APIs" in result
    assert "FastAPI" in result


def test_skills_are_categorized_correctly():
    result = categorize_skills(["Python", "Django", "Machine Learning"])

    assert result["Programming Languages"] == ["Python"]
    assert result["Web Technologies and Frameworks"] == ["Django"]
    assert result["AI and Machine Learning"] == ["Machine Learning"]


def test_sql_does_not_match_nosql():
    assert contains_skill("We use NoSQL databases.", "SQL") is False


def test_git_does_not_match_digital():
    assert contains_skill("The team works on digital products.", "Git") is False


def test_punctuation_does_not_prevent_skill_detection():
    result = extract_skills("Python, Django/Flask, and React.")

    assert "Python" in result
    assert "Django" in result
    assert "Flask" in result
    assert "React" in result


def test_repeated_skill_with_punctuation_is_detected_once():
    result = extract_skills("Python and PYTHON; Python.")

    assert result.count("Python") == 1


def test_react_aliases_produce_one_canonical_skill():
    result = extract_skills("React, React.js, and ReactJS")

    assert result.count("React") == 1


def test_postgres_alias_maps_to_postgresql():
    result = extract_skills("We use Postgres and PostgreSQL.")

    assert result.count("PostgreSQL") == 1


def test_cicd_punctuation_alias_is_detected():
    result = extract_skills("Experience with CI/CD pipelines")

    assert "CI/CD" in result


def test_debug_and_debugging_produce_one_canonical_skill():
    result = extract_skills("Debug applications and debugging issues")

    assert result.count("Debugging") == 1


def test_nodejs_alias_maps_to_nodejs_canonical_name():
    result = extract_skills("Experience with NODEJS")

    assert "Node.js" in result


def test_required_skill_context():
    assert (
        classify_skill_context("Python is required for this role.", "Python")
        == "required"
    )


def test_not_required_skill_context():
    assert (
        classify_skill_context("Python experience is not required.", "Python")
        == "not_required"
    )


def test_negated_skill_context():
    assert (
        classify_skill_context("We do not use Python.", "Python")
        == "negated"
    )


def test_preferred_skill_context():
    assert (
        classify_skill_context("Python is preferred.", "Python")
        == "preferred"
    )


def test_unclassified_skill_context():
    assert (
        classify_skill_context(
            "The team develops applications with Python.",
            "Python",
        )
        == "mentioned"
    )


def test_absent_skill_context():
    assert (
        classify_skill_context(
            "The team develops applications with Django.",
            "Python",
        )
        == "not_mentioned"
    )


def test_java_is_not_used_is_classified_as_negated():
    text = (
        "Python is not required, but JavaScript is preferred "
        "and Java is not used."
    )

    assert classify_skill_context(text, "Java") == "negated"


def test_negation_and_preference_are_classified_independently():
    text = "Python is not required, but JavaScript is preferred."

    assert classify_skill_context(text, "Python") == "not_required"
    assert classify_skill_context(text, "JavaScript") == "preferred"


def test_negated_python_does_not_affect_required_java():
    text = "We do not use Python, but Java is required."

    assert classify_skill_context(text, "Python") == "negated"
    assert classify_skill_context(text, "Java") == "required"


def test_separate_sentences_have_independent_contexts():
    text = "Python is required. JavaScript is not used."

    assert classify_skill_context(text, "Python") == "required"
    assert classify_skill_context(text, "JavaScript") == "negated"


def test_preferred_but_not_mandatory_is_preferred():
    text = "Python is preferred, not mandatory."

    assert classify_skill_context(text, "Python") == "preferred"


def test_extraction_results_include_skill_contexts(tmp_path):
    job = JobDescription(
        file="test_jd.txt",
        title="Python Developer",
        company="Example Company",
        location="Hyderabad",
        experience_min=0,
        experience_max=2,
        salary="Not specified",
        source="Test",
        url="",
        date_posted="",
        date_collected="",
        body="Python is required, but JavaScript is preferred.",
        path=tmp_path / "test_jd.txt",
    )

    result = extract_from_all_jds([job])[0]

    assert result["skill_contexts"]["Python"] == "required"
    assert result["skill_contexts"]["JavaScript"] == "preferred"
    assert "skills" in result
    assert "categories" in result

def test_extraction_results_classify_negated_skills(tmp_path):
    job = JobDescription(
        file="test_negation.txt",
        title="Software Developer",
        company="Example Company",
        location="Hyderabad",
        experience_min=0,
        experience_max=2,
        salary="Not specified",
        source="Test",
        url="",
        date_posted="",
        date_collected="",
        body="We do not use Python, but Java is required.",
        path=tmp_path / "test_negation.txt",
    )

    result = extract_from_all_jds([job])[0]

    assert result["skill_contexts"]["Python"] == "negated"
    assert result["skill_contexts"]["Java"] == "required"

def test_required_and_negated_skills_in_separate_sentences():
    text = "Python is required. Java is not used."

    assert classify_skill_context(text, "Python") == "required"
    assert classify_skill_context(text, "Java") == "negated"


def test_contexts_are_independent_across_three_sentences():
    text = (
        "Python is required. "
        "Java is not used. "
        "JavaScript is preferred."
    )

    assert classify_skill_context(text, "Python") == "required"
    assert classify_skill_context(text, "Java") == "negated"
    assert classify_skill_context(text, "JavaScript") == "preferred"


def test_conflicting_contexts_return_mixed():
    text = "Python is required. Python is not required."

    assert classify_skill_context(text, "Python") == "mixed"


def test_ordinary_mention_does_not_override_required_status():
    text = "Python is required. The team also works with Python."

    assert classify_skill_context(text, "Python") == "required"


def test_aliases_are_used_for_context_classification():
    text = "Fast API is required."

    assert classify_skill_context(
        text,
        "FastAPI",
        aliases=["FastAPI", "Fast API"],
    ) == "required"


def test_unrelated_sentence_does_not_change_skill_context():
    text = "Python is required. The office is located in Hyderabad."

    assert classify_skill_context(text, "Python") == "required"


def test_required_heading_classifies_all_skills_in_list():
    text = (
        "Languages Required: JavaScript; .NET; C#; "
        "HTML; CSS; AngularJS; Typescript; Python"
    )

    assert classify_skill_context(
        text, "Python", aliases=["Python"]
    ) == "required"

    assert classify_skill_context(
        text, "JavaScript", aliases=["JavaScript"]
    ) == "required"

    assert classify_skill_context(
        text, "HTML", aliases=["HTML"]
    ) == "required"


def test_preferred_heading_classifies_all_skills_in_list():
    text = "Languages preferred but not essential: C++; Java"

    assert classify_skill_context(
        text, "C++", aliases=["C++"]
    ) == "preferred"

    assert classify_skill_context(
        text, "Java", aliases=["Java"]
    ) == "preferred"


def test_required_heading_does_not_affect_next_line():
    text = (
        "Languages Required: Python; JavaScript\n"
        "Languages preferred but not essential: Java"
    )

    assert classify_skill_context(
        text, "Python", aliases=["Python"]
    ) == "required"

    assert classify_skill_context(
        text, "JavaScript", aliases=["JavaScript"]
    ) == "required"

    assert classify_skill_context(
        text, "Java", aliases=["Java"]
    ) == "preferred"


def test_sentence_context_still_works_after_line_splitting():
    text = "Python is required. Java is not used."

    assert classify_skill_context(text, "Python") == "required"
    assert classify_skill_context(text, "Java") == "negated"


def test_python_does_not_match_pythonista():
    assert extract_skills("Pythonista developers") == []


def test_mongo_db_alias_maps_to_mongodb():
    result = extract_skills("Experience with Mongo DB")

    assert result == ["MongoDB"]

def test_comma_separated_negation_does_not_affect_other_skill():
    text = "JavaScript, not Java."

    assert classify_skill_context(text, "Java") == "negated"
    assert classify_skill_context(text, "JavaScript") == "mentioned"