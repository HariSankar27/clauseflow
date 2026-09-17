from evals.run import _is_hit, regenerate_readme_table


def test_hit_when_answer_is_substring_of_prediction():
    assert _is_hit("This Agreement (the Affiliate Agreement)", ["Affiliate Agreement"])


def test_hit_when_prediction_is_substring_of_answer():
    assert _is_hit("Delaware", ["the State of Delaware"])


def test_no_hit_when_unrelated():
    assert not _is_hit("California", ["Delaware"])


def test_no_hit_when_prediction_is_none():
    assert not _is_hit(None, ["Delaware"])


def test_no_hit_when_no_expected_answers():
    assert not _is_hit("anything", [])


def test_match_is_case_insensitive():
    assert _is_hit("DELAWARE", ["delaware"])


def test_regenerate_readme_table_replaces_only_marked_section(monkeypatch, tmp_path):
    import evals.run as run_module

    readme = tmp_path / "README.md"
    readme.write_text(
        "# Title\n\n## Results\n\n<!-- eval-results:start -->\n"
        "old\n<!-- eval-results:end -->\n\n## Next\n"
    )
    monkeypatch.setattr(run_module, "README_PATH", readme)

    regenerate_readme_table(
        {
            "precision": 0.9,
            "recall": 0.8,
            "model": "gemini-2.5-flash",
            "documents": 7,
            "fields_scored": 35,
            "date": "2026-09-18",
        }
    )

    text = readme.read_text()
    assert "old" not in text
    assert "0.9" in text
    assert "## Next" in text
