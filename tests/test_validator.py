from dataclasses import replace

from joblens.loader import parse_jd
from joblens.validator import (
    find_duplicates,
    validate_all,
    validate_job,
)


def make_valid_job(tmp_path):
    """Create a valid sample job for testing."""
    jd_file = tmp_path / "jd_test.txt"

    jd_file.write_text(
        "TITLE: Python Developer\n"
        "COMPANY: Example Technologies\n"
        "LOCATION: Hyderabad, Telangana, India\n"
        "EXPERIENCE: 0-2 years\n"
        "SOURCE: LinkedIn\n"
        "URL: https://example.com/job\n"
        "---\n"
        "We are looking for a Python developer.\n",
        encoding="utf-8",
    )

    return parse_jd(jd_file)


def test_valid_job_has_no_errors(tmp_path):
    job = make_valid_job(tmp_path)

    result = validate_job(job)

    assert result.errors == []


def test_missing_company_is_an_error(tmp_path):
    job = make_valid_job(tmp_path)
    job = replace(job, company="")

    result = validate_job(job)

    assert any("company" in error for error in result.errors)


def test_empty_job_description_is_an_error(tmp_path):
    job = make_valid_job(tmp_path)
    job = replace(job, body="   ")

    result = validate_job(job)

    assert any("body is empty" in error for error in result.errors)


def test_invalid_experience_range_is_an_error(tmp_path):
    job = make_valid_job(tmp_path)
    job = replace(
        job,
        experience_min=3,
        experience_max=1,
    )

    result = validate_job(job)

    assert any("Invalid experience range" in error
               for error in result.errors)


def test_bengaluru_location_is_not_a_data_error(tmp_path):
    job = make_valid_job(tmp_path)
    job = replace(
        job,
        location="Bengaluru, Karnataka, India",
    )

    result = validate_job(job)

    assert result.errors == []
    assert not any("Location is outside" in warning
                   for warning in result.warnings)


def test_three_year_range_is_not_a_data_error(tmp_path):
    job = make_valid_job(tmp_path)
    job = replace(
        job,
        experience_min=0,
        experience_max=3,
    )

    result = validate_job(job)

    assert result.errors == []
    assert not any("Experience range extends beyond" in warning
                   for warning in result.warnings)


def test_duplicate_company_and_title_are_detected(tmp_path):
    first_job = make_valid_job(tmp_path)
    second_job = replace(first_job, file="jd_duplicate.txt")

    duplicates = find_duplicates([first_job, second_job])

    assert len(duplicates) == 1
    assert set(duplicates[0]) == {
        first_job.file,
        second_job.file,
    }


def test_unique_jobs_have_no_duplicates(tmp_path):
    first_job = make_valid_job(tmp_path)
    second_job = replace(
        first_job,
        file="jd_second.txt",
        company="Another Technologies",
    )

    assert find_duplicates([first_job, second_job]) == []
