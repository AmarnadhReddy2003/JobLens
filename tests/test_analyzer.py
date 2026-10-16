from joblens.analyzer import analyze_jobs
from joblens.loader import parse_jd


def make_job(tmp_path, filename, body):
    """Create a sample job description."""
    path = tmp_path / filename

    path.write_text(
        "TITLE: Python Developer\n"
        "COMPANY: Example Technologies\n"
        "LOCATION: Hyderabad\n"
        "SOURCE: LinkedIn\n"
        "URL: https://example.com/job\n"
        "---\n"
        f"{body}\n",
        encoding="utf-8",
    )

    return parse_jd(path)


def make_profile(tmp_path, content="Python\n"):
    """Create a profile file for the test."""
    path = tmp_path / "profile.txt"
    path.write_text(content, encoding="utf-8")
    return path


def test_skill_counted_once_per_job(tmp_path):
    job = make_job(
        tmp_path,
        "jd_001.txt",
        "Python Python Python development.",
    )
    profile = make_profile(tmp_path)

    report = analyze_jobs([job], profile)

    python = next(
        item for item in report["skill_frequency"]
        if item["skill"] == "Python"
    )

    assert python["jobs"] == 1
    assert python["percentage"] == 100.0


def test_skill_frequency_across_jobs(tmp_path):
    first = make_job(tmp_path, "jd_001.txt", "Python and Django.")
    second = make_job(tmp_path, "jd_002.txt", "Python development.")
    profile = make_profile(tmp_path)

    report = analyze_jobs([first, second], profile)

    python = next(
        item for item in report["skill_frequency"]
        if item["skill"] == "Python"
    )
    django = next(
        item for item in report["skill_frequency"]
        if item["skill"] == "Django"
    )

    assert python["jobs"] == 2
    assert python["percentage"] == 100.0
    assert django["jobs"] == 1
    assert django["percentage"] == 50.0


def test_profile_match_preserves_status(tmp_path):
    job = make_job(tmp_path, "jd_001.txt", "Python and Django.")
    profile = make_profile(
        tmp_path,
        "Python | know\nDjango | used\n",
    )

    report = analyze_jobs([job], profile)

    matches = {
        item["skill"]: item["status"]
        for item in report["profile_matches"]
    }

    assert matches["Python"] == "know"
    assert matches["Django"] == "used"


def test_unlisted_skill_is_marked_for_review(tmp_path):
    job = make_job(tmp_path, "jd_001.txt", "Python and Django.")
    profile = make_profile(tmp_path, "Python\n")

    report = analyze_jobs([job], profile)

    assert "Django" in report["skills_to_review"]


def test_empty_dataset_returns_zero_summary(tmp_path):
    profile = make_profile(tmp_path, "Python\n")

    report = analyze_jobs([], profile)

    assert report["summary"]["jobs_analyzed"] == 0
    assert report["summary"]["unique_skills"] == 0
    assert report["skill_frequency"] == []
    assert report["category_frequency"] == []