# JobLens — Job Market Skill Analyzer

JobLens is a Python-based project that analyzes locally collected job descriptions to identify frequently requested skills, summarize skill categories, and compare detected skills against a user-maintained skills profile.

It uses a modular architecture with separate components for data loading, validation, skill extraction, analysis, evaluation, and report generation.

## Problem Statement

Job seekers often find it difficult to determine which technical skills to prioritize when preparing for entry-level software development roles. Requirements vary across employers and positions, making it challenging to compare job-market expectations with existing skills.

JobLens addresses this problem by extracting recognized skills from collected job descriptions, calculating their frequency, grouping them into categories, and comparing them with a self-reported skills profile.

## Objectives

- Load and validate locally stored job descriptions.
- Extract recognized skills using a configurable dictionary and regular expressions.
- Calculate skill frequency across job descriptions.
- Group skills into meaningful categories.
- Compare detected skills with a user-maintained profile.
- Classify skill mentions by their context where supported by the implemented rules.
- Generate CSV and JSON reports.
- Test the project's components using automated tests.
- Evaluate skill extraction against manually specified expected results.

## Features

- **Job loading:** Parses job-description files and their metadata.
- **Data validation:** Checks required fields, experience ranges, and duplicate company-title combinations.
- **Skill extraction:** Uses case-insensitive matching and configurable aliases.
- **Frequency analysis:** Counts each recognized skill at most once per job description.
- **Category analysis:** Summarizes skill categories across the dataset.
- **Profile comparison:** Identifies detected skills listed in the profile and skills that are not listed.
- **Context analysis:** Classifies recognized skill mentions using rule-based patterns and supported headings.
- **Report generation:** Produces five CSV and JSON report files.
- **Extraction evaluation:** Compares extracted skills with manually specified expected results.
- **Automated testing:** Tests loading, validation, extraction, analysis, evaluation, and report generation.

## Technologies Used

- Python 3
- Regular expressions
- Dataclasses and `pathlib`
- `collections.Counter`
- CSV and JSON
- Pytest
- Git and GitHub

## Project Structure

```text
JobLens/
├── data/
│   ├── jds/
│   │   ├── jd_001.txt
│   │   └── ...
│   ├── evaluation/
│   │   └── expected_skills.json
│   └── skills.json
├── joblens/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── loader.py
│   ├── validator.py
│   ├── extractor.py
│   ├── analyzer.py
│   ├── evaluator.py
│   └── report_generator.py
├── reports/
│   └── v2/
│       ├── skill_frequency.csv
│       ├── category_frequency.csv
│       ├── skill_gap_report.csv
│       ├── skill_gap_report.json
│       └── skill_context_frequency.csv
├── tests/
│   ├── test_loader.py
│   ├── test_validator.py
│   ├── test_extractor.py
│   ├── test_analyzer.py
│   ├── test_evaluator.py
│   └── test_report_generator.py
├── my_skills.txt
├── Roles.txt
├── websites.txt
├── .gitignore
└── README.md
```

## How It Works

1. **Load:** Read job descriptions from `data/jds/`.
2. **Validate:** Check parsed records for supported data-quality issues.
3. **Extract:** Identify recognized skills using aliases configured in `data/skills.json`.
4. **Analyze:** Calculate skill and category frequencies and compare detected skills against `my_skills.txt`.
5. **Classify context:** Apply rule-based patterns to classify skill mentions where supported.
6. **Generate reports:** Save the analysis results in `reports/v2/`.
7. **Evaluate:** Compare extraction results against manually specified expected skills.
8. **Test:** Run the automated test suite to check the implemented behavior.

## Getting Started

### Prerequisites

- Python 3
- Git, if cloning the repository
- PowerShell, Command Prompt, or a terminal in VS Code

### 1. Clone the Repository

```powershell
git clone https://github.com/AmarnadhReddy2003/JobLens.git
cd JobLens
```

If you already have the project locally, open the `JobLens` root directory in your terminal.

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use the virtual environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
```

### 3. Install the Testing Dependency

```powershell
python -m pip install pytest
```

The core project uses Python's standard library. Pytest is required to run the automated test suite.

### 4. Validate the Dataset

```powershell
python -m joblens.validator
```

### 5. Run Skill Analysis

```powershell
python -m joblens.analyzer
```

### 6. Generate Reports

```powershell
python -m joblens.report_generator
```

The reports are written to `reports/v2/`. Running the report generator again updates those files.

### 7. Run the Tests

Run the complete test suite:

```powershell
python -m pytest -v
```

To run an individual test module:

```powershell
python -m pytest tests/test_extractor.py -v
```

**Verified test result:** The current project test suite completed with **77 passed in 2.20 seconds** in the reported local run. Your result may differ if the code or test suite changes.

## Output Reports

All five reports are saved under `reports/v2/`.

| Report | Description |
|---|---|
| `skill_frequency.csv` | Each detected skill's job count and percentage. |
| `category_frequency.csv` | Job counts and percentages for each skill category. |
| `skill_gap_report.csv` | Detected skills, frequency, profile status, and classification. |
| `skill_gap_report.json` | Structured analysis results, including summary, per-job results, profile comparisons, and load failures. |
| `skill_context_frequency.csv` | Counts and percentages for detected skill-context combinations. |

### Understanding the Results

- **Skill frequency:** Counts how many job descriptions contain each recognized skill. Each skill is counted at most once per job.
- **Category frequency:** Counts the job descriptions containing at least one skill belonging to each configured category.
- **Profile match:** Indicates that a detected skill is listed in `my_skills.txt`.
- **To review:** Indicates that a detected skill is not listed in the current profile file. It does not mean the user lacks that skill.
- **Skill context:** Describes the classification produced by the implemented rule-based context analyzer.

## Current Sample Results

The current dataset contains 10 job descriptions.

| Skill | Jobs mentioning it | Frequency |
|---|---:|---:|
| Python | 9 of 10 | 90% |
| Software Development | 8 of 10 | 80% |
| Problem Solving | 7 of 10 | 70% |
| Troubleshooting | 6 of 10 | 60% |
| Communication | 6 of 10 | 60% |

The current analysis detects 47 unique skills, with 12 profile matches and 35 skills to review.

These figures describe the current local dataset and may change when job descriptions, skill aliases, or profile entries change.

## Data Collection and Limitations

- **Sample size:** 10 job descriptions.
- **Sources:** LinkedIn and Naukri, as recorded in the collected dataset.
- **Target location:** Primarily Hyderabad, Telangana, with an individual posting recorded in Bengaluru.
- **Target experience:** Primarily fresher and entry-level opportunities.
- **Collection period:** 7 January 2026 to 14 October 2026.

The descriptions are stored locally. JobLens does not automatically collect live job postings.

The dataset contains a mixture of software development, Python-related, and adjacent technical roles. One retained advertisement includes both IT and non-IT hiring. These factors can influence the results.

**Metadata verification:** JD-007's stored location and experience details may differ from the original posting. These details should be verified against the source before changing the stored metadata.

Other limitations include:

- A small sample cannot represent the entire job market.
- Dictionary-based extraction can miss unfamiliar aliases and contextual variations.
- A detected mention does not automatically establish whether a skill is mandatory or preferred.
- Rule-based context classification may not correctly interpret every heading, sentence, or negation pattern.
- Skill frequencies reflect this dataset, not universal employer demand.
- Profile comparisons depend on the accuracy and completeness of `my_skills.txt`.
- Automated tests cover selected behaviors but do not establish comprehensive extraction precision, recall, or F1 performance on real-world job descriptions.

The results should be treated as exploratory findings rather than definitive estimates of market demand or assessments of an individual's abilities.

## Future Improvements

- Expand the dataset with more verified job descriptions.
- Improve skill aliases and contextual matching.
- Add role-specific comparisons.
- Evaluate extraction precision and recall against a larger manually annotated dataset.
- Improve filtering by location, experience, and job type.
- Add visualizations for skill and category frequencies.

## Author

**Amaranadha Reddy Thallapureddy**

- GitHub profile: [AmarnadhReddy2003](https://github.com/AmarnadhReddy2003)
- Project repository: [JobLens](https://github.com/AmarnadhReddy2003/JobLens)
