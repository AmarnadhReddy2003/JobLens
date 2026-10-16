from joblens.loader import parse_experience, parse_jd


def test_parse_freshers_experience():
    assert parse_experience("Freshers") == (0, 0)


def test_parse_experience_range_with_hyphen():
    assert parse_experience("0-2 years") == (0, 2)


def test_parse_experience_range_with_to():
    assert parse_experience("0 to 3 years") == (0, 3)


def test_parse_open_ended_experience():
    assert parse_experience("2+ years") == (2, None)


def test_parse_exact_experience():
    assert parse_experience("2 years") == (2, 2)


def test_parse_unknown_experience():
    assert parse_experience("Not specified") == (None, None)


def test_parse_jd_requires_separator_line(tmp_path):
    jd_file = tmp_path / "jd_999.txt"
    jd_file.write_text(
        "TITLE: Example Engineer\n"
        "COMPANY: Example Corp\n"
        "---\n"
        "Python and SQL are used here.\n",
        encoding="utf-8",
    )

    job = parse_jd(jd_file)

    assert job.title == "Example Engineer"
    assert job.company == "Example Corp"
    assert job.body == "Python and SQL are used here."


def test_parse_jd_rejects_missing_separator(tmp_path):
    jd_file = tmp_path / "jd_999.txt"
    jd_file.write_text(
        "TITLE: Example Engineer\n"
        "Description includes --- inside the text.",
        encoding="utf-8",
    )

    try:
        parse_jd(jd_file)
    except ValueError as error:
        assert "separator line" in str(error)
    else:
        raise AssertionError("Expected ValueError for missing separator")
