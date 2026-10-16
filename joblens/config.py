
from pathlib import Path

# Root directory of the JobLens project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
JDS_DIR = DATA_DIR / "jds"
LABELS_DIR = DATA_DIR / "labels"
SOURCES_DIR = DATA_DIR / "sources"

# Reports
REPORTS_DIR = PROJECT_ROOT / "reports"

# User and source files
MY_SKILLS_FILE = PROJECT_ROOT / "my_skills.txt"
ROLES_FILE = PROJECT_ROOT / "Roles.txt"
WEBSITES_FILE = PROJECT_ROOT / "websites.txt"

# Analysis defaults
MAX_EXPERIENCE_YEARS = 2
TOP_N_DEFAULT = 10
