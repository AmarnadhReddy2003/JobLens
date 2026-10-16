
import json
from pathlib import Path

from joblens.config import DATA_DIR
from joblens.extractor import extract_skills, load_skill_config


EVALUATION_FILE = DATA_DIR / "evaluation" / "expected_skills.json"


def load_evaluation_cases(path: str | Path = EVALUATION_FILE) -> list[dict]:
    """Load manually checked skill evaluation cases."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    cases = data.get("cases")

    if not isinstance(cases, list):
        raise ValueError("Evaluation file must contain a 'cases' list.")

    for case in cases:
        if (
            not isinstance(case, dict)
            or not isinstance(case.get("id"), str)
            or not isinstance(case.get("description"), str)
            or not isinstance(case.get("expected_skills"), list)
        ):
            raise ValueError(f"Invalid evaluation case: {case!r}")

    return cases


def evaluate_extractor(
    cases: list[dict],
    skill_dictionary: dict[str, list[str]] | None = None,
) -> dict:
    """Compare extracted skills with manually expected skills."""
    if skill_dictionary is None:
        skill_dictionary, _ = load_skill_config()

    total_expected = 0
    total_predicted = 0
    total_correct = 0
    results = []

    for case in cases:
        expected = set(case["expected_skills"])
        predicted = set(
            extract_skills(case["description"], skill_dictionary)
        )

        correct = expected & predicted
        false_positives = predicted - expected
        false_negatives = expected - predicted

        total_expected += len(expected)
        total_predicted += len(predicted)
        total_correct += len(correct)

        results.append({
            "id": case["id"],
            "expected": sorted(expected),
            "predicted": sorted(predicted),
            "correct": sorted(correct),
            "false_positives": sorted(false_positives),
            "false_negatives": sorted(false_negatives),
        })

    precision = (
        total_correct / total_predicted
        if total_predicted else 0.0
    )
    recall = (
        total_correct / total_expected
        if total_expected else 0.0
    )
    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "cases_evaluated": len(cases),
        "correct_detections": total_correct,
        "predicted_skills": total_predicted,
        "expected_skills": total_expected,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "results": results,
    }


def main() -> None:
    cases = load_evaluation_cases()
    report = evaluate_extractor(cases)

    print("JOBLENS — EXTRACTOR EVALUATION")
    print(f"Cases evaluated: {report['cases_evaluated']}")
    print(f"Expected skills: {report['expected_skills']}")
    print(f"Predicted skills: {report['predicted_skills']}")
    print(f"Correct detections: {report['correct_detections']}")
    print(f"Precision: {report['precision']:.2%}")
    print(f"Recall: {report['recall']:.2%}")
    print(f"F1 score: {report['f1_score']:.2%}")

    for result in report["results"]:
        print(f"\n{result['id']}")
        print(f"  Correct: {result['correct']}")
        print(f"  False positives: {result['false_positives']}")
        print(f"  False negatives: {result['false_negatives']}")


if __name__ == "__main__":
    main()
