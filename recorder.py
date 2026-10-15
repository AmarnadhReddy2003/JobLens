
from urllib.parse import urlparse

from loader import load_all


REQUIRED_FIELDS = [
    "TITLE",
    "COMPANY",
    "LOCATION",
    "EXPERIENCE",
    "SOURCE",
    "DATE_COLLECTED"
]


def validate_jds(job_descriptions):
    issues = []
    seen_urls = {}

    for jd in job_descriptions:
        filename = jd.get("file", "Unknown file")
        meta = jd["meta"]

        # Check required metadata fields
        for field in REQUIRED_FIELDS:
            value = meta.get(field, "")

            if not value.strip():
                issues.append({
                    "file": filename,
                    "issue": f"Missing required field: {field}"
                })

        # Check URL
        url = meta.get("URL", "").strip()

        if not url:
            issues.append({
                "file": filename,
                "issue": "Missing URL"
            })

        else:
            parsed_url = urlparse(url)

            if (
                parsed_url.scheme not in ("http", "https")
                or not parsed_url.netloc
            ):
                issues.append({
                    "file": filename,
                    "issue": "Invalid URL format"
                })

            # Check for duplicate URLs
            normalized_url = url.rstrip("/").lower()

            if normalized_url in seen_urls:
                issues.append({
                    "file": filename,
                    "issue": (
                        "Duplicate URL also found in "
                        f"{seen_urls[normalized_url]}"
                    )
                })
            else:
                seen_urls[normalized_url] = filename

        # Check posting date
        if not meta.get("DATE_POSTED", "").strip():
            issues.append({
                "file": filename,
                "issue": "Missing posting date"
            })

    return issues


if __name__ == "__main__":
    job_descriptions = load_all()

    issues = validate_jds(job_descriptions)

    print("\nJOBLENS DATA VALIDATION")
    print("-----------------------")
    print("Total JDs loaded:", len(job_descriptions))
    print("Total issues found:", len(issues))

    if issues:
        print("\nIssues:")

        for issue in issues:
            print(
                f'- {issue["file"]}: {issue["issue"]}'
            )
    else:
        print("All checks passed.")
