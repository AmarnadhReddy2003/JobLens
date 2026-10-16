from joblens.extractor import (
    categorize_skills,
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