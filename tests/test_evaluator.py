
import pytest

from joblens.evaluator import evaluate_extractor


def fake_extractor(text, skill_dictionary):
    """Return controlled predictions for evaluator unit tests."""
    return {
        "perfect": ["Python"],
        "false_positive": ["Python", "Django"],
        "false_negative": ["Python"],
        "no_predictions": [],
        "no_expected": ["Python"],
        "no_skills": [],
    }[text]


SKILL_DICTIONARY = {
    "Python": ["python"],
    "Django": ["django"],
}


def run_evaluation(monkeypatch, case, prediction_key):
    from joblens import evaluator

    monkeypatch.setattr(
        evaluator,
        "extract_skills",
        lambda text, skill_dictionary: fake_extractor(
            prediction_key, skill_dictionary
        ),
    )

    return evaluate_extractor([case], SKILL_DICTIONARY)


def test_perfect_prediction(monkeypatch):
    report = run_evaluation(
        monkeypatch,
        {"id": "test_001", "description": "perfect", "expected_skills": ["Python"]},
        "perfect",
    )

    assert report["correct_detections"] == 1
    assert report["precision"] == 1.0
    assert report["recall"] == 1.0
    assert report["f1_score"] == 1.0


def test_false_positive_is_counted(monkeypatch):
    report = run_evaluation(
        monkeypatch,
        {"id": "test_002", "description": "false_positive", "expected_skills": ["Python"]},
        "false_positive",
    )

    result = report["results"][0]

    assert result["correct"] == ["Python"]
    assert result["false_positives"] == ["Django"]
    assert result["false_negatives"] == []
    assert report["precision"] == pytest.approx(0.5)
    assert report["recall"] == 1.0
    assert report["f1_score"] == pytest.approx(2 / 3)


def test_false_negative_is_counted(monkeypatch):
    report = run_evaluation(
        monkeypatch,
        {
            "id": "test_003",
            "description": "false_negative",
            "expected_skills": ["Python", "Django"],
        },
        "false_negative",
    )

    result = report["results"][0]

    assert result["correct"] == ["Python"]
    assert result["false_positives"] == []
    assert result["false_negatives"] == ["Django"]
    assert report["precision"] == 1.0
    assert report["recall"] == pytest.approx(0.5)
    assert report["f1_score"] == pytest.approx(2 / 3)


def test_no_predictions_does_not_crash(monkeypatch):
    report = run_evaluation(
        monkeypatch,
        {"id": "test_004", "description": "no_predictions", "expected_skills": ["Python"]},
        "no_predictions",
    )

    assert report["precision"] == 0.0
    assert report["recall"] == 0.0
    assert report["f1_score"] == 0.0
    assert report["results"][0]["false_negatives"] == ["Python"]


def test_no_expected_skills_counts_false_positive(monkeypatch):
    report = run_evaluation(
        monkeypatch,
        {"id": "test_005", "description": "no_expected", "expected_skills": []},
        "no_expected",
    )

    assert report["precision"] == 0.0
    assert report["recall"] == 0.0
    assert report["f1_score"] == 0.0
    assert report["results"][0]["false_positives"] == ["Python"]


def test_empty_expected_and_predicted_skills(monkeypatch):
    report = run_evaluation(
        monkeypatch,
        {"id": "test_006", "description": "no_skills", "expected_skills": []},
        "no_skills",
    )

    assert report["precision"] == 0.0
    assert report["recall"] == 0.0
    assert report["f1_score"] == 0.0
    assert report["results"][0]["correct"] == []
