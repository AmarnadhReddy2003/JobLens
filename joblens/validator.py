from collections import defaultdict
from dataclasses import dataclass, field

from joblens.loader import LoadResult, load_all
from joblens.models import JobDescription


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


@dataclass
class ValidationReport:
    results: dict[str, ValidationResult]
    duplicate_groups: list[list[str]]

    @property
    def total_errors(self) -> int:
        return sum(
            len(result.errors)
            for result in self.results.values()
        )

    @property
    def total_warnings(self) -> int:
        return sum(
            len(result.warnings)
            for result in self.results.values()
        )


def validate_job(job: JobDescription) -> ValidationResult:
    """Check data quality without enforcing job-search preferences."""
    result = ValidationResult()

    # Check required metadata.
    required_fields = {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "source": job.source,
        "url": job.url,
    }

    for field_name, value in required_fields.items():
        if not value or not value.strip():
            result.errors.append(
                f"Missing required field: {field_name}"
            )

    # Check the description body.
    if not job.body or not job.body.strip():
        result.errors.append("Job description body is empty.")

    # Check experience data only for consistency.
    minimum = job.experience_min
    maximum = job.experience_max

    if (
        minimum is not None
        and maximum is not None
        and minimum > maximum
    ):
        result.errors.append(
            "Invalid experience range: minimum exceeds maximum."
        )

    if minimum is None and maximum is None:
        result.warnings.append(
            "Experience requirement is missing or could not be parsed."
        )

    # Location and experience preferences are deliberately not checked
    # here. A valid job can be outside the user's preferred criteria.

    return result


def find_duplicates(
    jobs: list[JobDescription],
) -> list[list[str]]:
    """Find jobs with matching normalized company names and titles."""
    grouped_files = defaultdict(list)

    for job in jobs:
        company = job.company.strip().casefold()
        title = job.title.strip().casefold()

        if company and title:
            grouped_files[(company, title)].append(job.file)

    return [
        filenames
        for filenames in grouped_files.values()
        if len(filenames) > 1
    ]


def validate_all(
    jobs: list[JobDescription],
) -> ValidationReport:
    """Validate jobs and report possible duplicates."""
    results = {
        job.file: validate_job(job)
        for job in jobs
    }

    duplicate_groups = find_duplicates(jobs)

    for filenames in duplicate_groups:
        message = (
            "Possible duplicate posting: "
            + ", ".join(filenames)
        )

        for filename in filenames:
            results[filename].warnings.append(message)

    return ValidationReport(
        results=results,
        duplicate_groups=duplicate_groups,
    )


def main() -> None:
    """Load job descriptions and print a concise validation report."""
    load_result: LoadResult = load_all()

    print("JOBLENS V2 — VALIDATOR")
    print("========================")

    if load_result.failures:
        print(f"Load failures: {len(load_result.failures)}")

        for failure in load_result.failures:
            print(f"  ERROR: {failure}")

    jobs = load_result.jobs

    if not jobs:
        print("No job descriptions available to validate.")
        return

    report = validate_all(jobs)

    valid_count = sum(
        result.is_valid
        for result in report.results.values()
    )
    invalid_count = len(report.results) - valid_count

    print(f"Jobs checked: {len(jobs)}")
    print(f"Passed data checks: {valid_count}")
    print(f"Failed data checks: {invalid_count}")
    print(f"Errors: {report.total_errors}")
    print(f"Warnings: {report.total_warnings}")
    print(f"Duplicate groups: {len(report.duplicate_groups)}")

    for job in jobs:
        result = report.results[job.file]

        if result.errors or result.warnings:
            print(
                f"\n{job.file} | "
                f"{job.company} | {job.title}"
            )

            for error in result.errors:
                print(f"  ERROR: {error}")

            for warning in result.warnings:
                print(f"  WARNING: {warning}")

    print("\nValidation complete.")


if __name__ == "__main__":
    main()
