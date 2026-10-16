
import csv
import json

from joblens import report_generator


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))



def test_all_five_report_files_are_created(tmp_path, monkeypatch):
    monkeypatch.setattr(report_generator, "REPORTS_DIR", tmp_path)

    report_generator.generate_reports()

    output_dir = tmp_path / "v2"

    expected_files = {
        "skill_frequency.csv",
        "category_frequency.csv",
        "skill_gap_report.csv",
        "skill_gap_report.json",
        "skill_context_frequency.csv",
    }

    actual_files = {path.name for path in output_dir.iterdir()}

    assert actual_files == expected_files


def test_csv_headers_are_correct(tmp_path, monkeypatch):
    monkeypatch.setattr(report_generator, "REPORTS_DIR", tmp_path)

    report_generator.generate_reports()

    output_dir = tmp_path / "v2"

    skill_rows = read_csv(output_dir / "skill_frequency.csv")
    category_rows = read_csv(output_dir / "category_frequency.csv")
    gap_rows = read_csv(output_dir / "skill_gap_report.csv")

    assert list(skill_rows[0].keys()) == [
        "skill", "jobs", "percentage"
    ]

    assert list(category_rows[0].keys()) == [
        "category", "jobs", "percentage"
    ]

    assert list(gap_rows[0].keys()) == [
        "skill",
        "jobs",
        "percentage",
        "profile_status",
        "classification",
    ]


def test_python_frequency_is_written_correctly(tmp_path, monkeypatch):
    monkeypatch.setattr(report_generator, "REPORTS_DIR", tmp_path)

    report_generator.generate_reports()

    rows = read_csv(tmp_path / "v2" / "skill_frequency.csv")

    python_row = next(row for row in rows if row["skill"] == "Python")

    assert python_row["jobs"] == "9"
    assert python_row["percentage"] == "90.0"


def test_json_summary_contains_expected_values(tmp_path, monkeypatch):
    monkeypatch.setattr(report_generator, "REPORTS_DIR", tmp_path)

    report_generator.generate_reports()

    path = tmp_path / "v2" / "skill_gap_report.json"

    with path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert report["summary"]["jobs_analyzed"] == 10
    assert report["summary"]["unique_skills"] == 47
    assert report["summary"]["profile_matches"] == 12
    assert report["summary"]["skills_to_review"] == 35


def test_output_directory_is_created_when_missing(tmp_path, monkeypatch):
    reports_dir = tmp_path / "new_reports"

    monkeypatch.setattr(report_generator, "REPORTS_DIR", reports_dir)

    assert not (reports_dir / "v2").exists()

    report_generator.generate_reports()

    assert (reports_dir / "v2").is_dir()

def test_skill_context_csv_headers_are_correct():
    from joblens.report_generator import generate_reports
    from joblens.config import REPORTS_DIR
    import csv

    generate_reports()

    report_path = (
        REPORTS_DIR / "v2" / "skill_context_frequency.csv"
    )

    with report_path.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.reader(file)
        headers = next(reader)

    assert headers == ["skill", "context", "jobs", "percentage"]