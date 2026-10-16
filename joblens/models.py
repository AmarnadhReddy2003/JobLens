
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JobDescription:
    file: str
    title: str
    company: str
    location: str
    experience_min: int | None
    experience_max: int | None
    salary: str
    source: str
    url: str
    date_posted: str
    date_collected: str
    body: str
    path: Path
