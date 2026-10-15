# JobLens — Job Market Skill Analyzer

JobLens is a Python-based project that analyzes collected job descriptions to identify frequently requested skills and compare them with a user's self-reported skill profile. It helps explore hiring patterns within a sample of entry-level and related software development roles.

## Problem Statement

Job seekers often find it difficult to determine which technical skills to prioritize when preparing for entry-level software development roles. Requirements vary across employers and positions, making it challenging to compare job-market expectations with existing skills.

JobLens addresses this problem by extracting recognized skills from collected job descriptions, calculating their frequency, grouping them into categories, and comparing them against a user-maintained skills profile.

## Objectives

- Analyze a collection of job descriptions using Python.
- Extract recognized skills using a curated skill dictionary and regular expressions.
- Calculate how frequently each skill appears across job descriptions.
- Group skills into meaningful categories.
- Compare detected skills against a self-reported skills profile.
- Generate CSV, JSON, and plain-text reports.
- Validate the structure of collected job-description data.

## Features

- **Job Description Loading:** Reads locally stored job descriptions from text files.
- **Data Validation:** Checks collected job-description files for supported structural issues.
- **Skill Extraction:** Identifies recognized skills using keyword aliases and case-insensitive regular expressions.
- **Skill Frequency Analysis:** Counts each recognized skill at most once per job description.
- **Category Analysis:** Groups skills into categories such as programming languages, databases, web technologies, AI and machine learning, development tools, and software engineering concepts.
- **Skill-Gap Analysis:** Compares detected skills with the skills listed in `my_skills.txt`.
- **Report Generation:** Exports results into CSV, JSON, and plain-text formats.
- **Extraction Tests:** Tests selected dictionary-matching behaviors, including capitalization, punctuation, special characters, and partial-word matching.

## Technologies Used

- Python 3
- Regular expressions (`re`)
- File handling and text processing
- `collections.Counter` for frequency analysis
- CSV and JSON
- Git and GitHub

## Project Structure

```text
JobLens/
├── data/
│   └── jds/
│       ├── jd_001.txt
│       ├── jd_002.txt
│       ├── ...
│       └── jd_010.txt
├── reports/
│   ├── skill_frequency.csv
│   ├── category_frequency.csv
│   ├── skill_gap_report.csv
│   ├── skill_gap_report.json
│   └── joblens_report.txt
├── Roles.txt
├── websites.txt
├── my_skills.txt
├── loader.py
├── recorder.py
├── skill_extractor.py
├── skill_analyzer.py
├── skill_gap_analyzer.py
├── report_generator.py
├── test_skill_extractor.py
├── .gitignore
└── README.md
```

The reports directory is generated or updated when the report generator runs.

## Main Components

| File | Purpose |
|---|---|
| `loader.py` | Loads job descriptions from `data/jds/`. |
| `recorder.py` | Validates the collected job-description data for supported structural issues. |
| `skill_extractor.py` | Extracts recognized skills using a curated dictionary and regular expressions. |
| `skill_analyzer.py` | Calculates skill frequencies and summarizes results by category. |
| `skill_gap_analyzer.py` | Compares detected job-market skills with the user's self-reported profile. |
| `report_generator.py` | Generates CSV, JSON, and plain-text reports. |
| `test_skill_extractor.py` | Tests selected skill-extraction behaviors. |
| `my_skills.txt` | Stores the user's self-reported skills. |
| `Roles.txt` | Records the roles considered during data collection. |
| `websites.txt` | Records the job-source websites used during data collection. |
| `data/jds/jd_*.txt` | Stores the collected job descriptions. |

## How It Works

1. **Data Collection:** Selected job descriptions are collected and stored as text files.
2. **Data Loading:** `loader.py` reads the files from `data/jds/` and extracts their metadata and description text.
3. **Data Validation:** `recorder.py` checks the collected data for supported structural issues.
4. **Skill Extraction:** `skill_extractor.py` searches job-description text for recognized skill aliases using case-insensitive regular expressions.
5. **Frequency Analysis:** `skill_analyzer.py` counts each detected skill once per job description and calculates its frequency across the dataset.
6. **Skill-Gap Analysis:** `skill_gap_analyzer.py` compares detected skills with the profile in `my_skills.txt`.
7. **Report Generation:** `report_generator.py` generates reports for further review.

## Getting Started

### Prerequisites

- Python 3 installed
- Git (optional, for cloning the repository)
- A terminal such as PowerShell or the VS Code terminal

### 1. Clone the Repository

```bash
git clone https://github.com/AmarnadhReddy2003/JobLens.git
cd JobLens
```

Alternatively, download the repository and open the project directory in VS Code.

Run the commands below from the project root directory.

### 2. Validate the Collected Data

```bash
python recorder.py
```

Review the output for any reported validation issues.

### 3. Run the Extraction Tests

```bash
python test_skill_extractor.py
```

This runs the existing tests for selected dictionary-matching behaviors.

### 4. Analyze Skill Frequencies

```bash
python skill_analyzer.py
```

This displays the number of job descriptions analyzed, the most frequently detected skills, category summaries, and the complete skill analysis.

### 5. Analyze Your Skill Gaps

```bash
python skill_gap_analyzer.py
```

This compares detected skills against `my_skills.txt` and groups them into confirmed profile matches and skills to review or learn.

A skill placed in the review-or-learn category is not confirmed in the supplied profile. It does not necessarily mean the user lacks that skill.

### 6. Generate Reports

```bash
python report_generator.py
```

The generated reports are saved in the `reports/` directory.

If `python` is not recognized on your system, try `py` instead.

## Output Reports

| Report | Description |
|---|---|
| `skill_frequency.csv` | Frequency results for individual detected skills. |
| `category_frequency.csv` | Frequency results grouped by skill category. |
| `skill_gap_report.csv` | Tabular comparison of detected skills with the user's profile. |
| `skill_gap_report.json` | Structured JSON version of the skill-gap results. |
| `joblens_report.txt` | Readable summary of the analysis. |

## Sample Results

For the current dataset of 10 job descriptions, JobLens reports the following frequently detected skills:

| Skill | Job descriptions mentioning it | Frequency |
|---|---:|---:|
| Python | 9 out of 10 | 90% |
| Software Development | 8 out of 10 | 80% |
| Problem Solving | 7 out of 10 | 70% |
| Troubleshooting | 6 out of 10 | 60% |
| Communication | 6 out of 10 | 60% |

The current skill-gap analysis identifies 12 detected skills as matches for the supplied profile and places 35 other detected skills in the review-or-learn category.

These figures describe the current dataset and profile. They are not universal estimates of employer demand or a definitive assessment of the user's abilities.

## Limitations

- The analysis is based on a sample of 10 collected job descriptions.
- The sample may not represent all employers, industries, locations, or entry-level technical roles.
- Skill extraction relies on a curated dictionary and keyword matching. Skills expressed using unrecognized wording may be missed.
- Keyword matching does not fully understand context. Detecting a skill mention does not establish whether an employer considers that skill mandatory.
- A skill listed for review is not confirmed in the supplied profile; this does not prove the user lacks that skill.
- Skill frequency alone does not determine the importance of a skill for a particular job.
- The project analyzes locally stored job descriptions and does not automatically collect live job postings.
- The existing extraction tests cover selected cases but do not establish comprehensive extraction accuracy across the entire dataset.

## Future Improvements

- Expand the dataset with more job descriptions from different employers and roles.
- Improve skill extraction to recognize additional aliases and contextual variations.
- Distinguish technical skills, development tools, and general professional competencies more clearly.
- Add visualizations for skill frequencies and category comparisons.
- Introduce role-specific comparisons and configurable skill profiles.
- Evaluate extraction precision and recall against manually reviewed job descriptions.

## Author

**Amaranadha Reddy Thallapureddy**

- GitHub Profile: https://github.com/AmarnadhReddy2003
- Project Repository: https://github.com/AmarnadhReddy2003/JobLens
