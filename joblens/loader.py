import re
from dataclasses import dataclass
from pathlib import Path

from joblens.config import JDS_DIR
from joblens.models import JobDescription


@dataclass
class LoadResult:
    jobs: list[JobDescription]
    failures: list[str]


def parse_experience(value: str) -> tuple[int | None, int | None]:
    """Extract minimum and maximum years from common experience formats."""
    text = value.strip().lower()

    if not text:
        return None, None

    # Handle fresher-related descriptions.
    if "fresher" in text:
        return 0, 0

    # Handle ranges such as "0-2 years", "0–2 years", and "0 to 3 years".
    match = re.search(
        r"(\d+)\s*(?:-|–|to)\s*(\d+)\s*(?:years?|yrs?)?",
        text,
    )
    if match:
        minimum, maximum = map(int, match.groups())
        return minimum, maximum

    # Handle open-ended formats such as "2+ years".
    match = re.search(
        r"(\d+)\s*\+\s*(?:years?|yrs?)",
        text,
    )
    if match:
        minimum = int(match.group(1))
        return minimum, None

    # Handle exact formats such as "2 years" or "1 yr".
    match = re.search(
        r"(\d+)\s*(?:years?|yrs?)",
        text,
    )
    if match:
        years = int(match.group(1))
        return years, years

    return None, None


def parse_jd(path: str | Path) -> JobDescription:
    """Parse one job description file into a JobDescription object."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")

    lines = text.splitlines()

    separator_index = next(
        (i for i, line in enumerate(lines) if line.strip() == "---"),
        None,
    )

    if separator_index is None:
        raise ValueError("Missing separator line '---'")

    header_lines = lines[:separator_index]
    body = "\n".join(lines[separator_index + 1:]).strip()

    metadata = {}

    for line in header_lines:
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        metadata[key.strip().upper()] = value.strip()

    experience_min, experience_max = parse_experience(
        metadata.get("EXPERIENCE", "")
    )

    return JobDescription(
        file=path.name,
        title=metadata.get("TITLE", ""),
        company=metadata.get("COMPANY", ""),
        location=metadata.get("LOCATION", ""),
        experience_min=experience_min,
        experience_max=experience_max,
        salary=metadata.get("SALARY", ""),
        source=metadata.get("SOURCE", ""),
        url=metadata.get("URL", ""),
        date_posted=metadata.get("DATE_POSTED", ""),
        date_collected=metadata.get("DATE_COLLECTED", ""),
        body=body,
        path=path,
    )


def load_all(folder: str | Path | None = None) -> LoadResult:
    """Load all JD files and record any files that fail to parse."""
    folder_path = Path(folder) if folder is not None else JDS_DIR

    jobs = []
    failures = []

    if not folder_path.is_dir():
        return LoadResult(
            jobs=[],
            failures=[f"JD directory does not exist: {folder_path}"],
        )

    paths = sorted(folder_path.glob("jd_*.txt"))

    for path in paths:
        try:
            jobs.append(parse_jd(path))
        except (ValueError, OSError, UnicodeError) as error:
            failures.append(f"{path.name}: {error}")

    return LoadResult(jobs=jobs, failures=failures)


if __name__ == "__main__":
    result = load_all()

    print("JOBLENS V2 — LOADER")
    print(f"Loaded: {len(result.jobs)} | Failed: {len(result.failures)}")

    for job in result.jobs:
        print(
            f"{job.file} | "
            f"{job.company or 'Unknown'} | "
            f"{job.title or 'Unknown'}"
        )

    for failure in result.failures:
        print(f"ERROR: {failure}")