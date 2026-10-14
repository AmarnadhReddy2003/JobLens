
from pathlib import Path


def parse_jd(path):
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    parts = text.split("---", 1)

    if len(parts) != 2:
        raise ValueError(
            f"Missing '---' separator in file: {path}"
        )

    header = parts[0]
    body = parts[1]

    meta = {}

    for line in header.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)

            # Normalize metadata keys to uppercase
            key = key.strip().upper()
            value = value.strip()

            meta[key] = value

    return {
        "meta": meta,
        "body": body.strip()
    }


def load_all(folder="."):
    folder_path = Path(folder)
    job_descriptions = []

    paths = sorted(folder_path.glob("jd_*.txt"))

    if not paths:
        print("No JD files found.")

    for path in paths:
        try:
            result = parse_jd(path)
            result["file"] = path.name
            job_descriptions.append(result)

        except (ValueError, OSError) as error:
            print(f"Could not load {path.name}: {error}")

    return job_descriptions


if __name__ == "__main__":
    job_descriptions = load_all(".")

    print("\nJOBLENS DATA LOADER")
    print("-------------------")
    print("Total JDs loaded:", len(job_descriptions))

    for jd in job_descriptions:
        meta = jd["meta"]

        print(
            jd["file"],
            "|",
            meta.get("COMPANY", "Unknown"),
            "|",
            meta.get("TITLE", "Unknown")
        )
