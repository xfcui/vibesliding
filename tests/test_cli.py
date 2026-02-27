import pytest
import click
from pathlib import Path
from src.cli import parse_page_spec, expand_article_paths

def test_parse_page_spec_single():
    assert parse_page_spec("1") == {1}
    assert parse_page_spec("5") == {5}

def test_parse_page_spec_list():
    assert parse_page_spec("1,3,5") == {1, 3, 5}
    assert parse_page_spec(" 1 , 3 , 5 ") == {1, 3, 5}

def test_parse_page_spec_range():
    assert parse_page_spec("1-3") == {1, 2, 3}
    assert parse_page_spec("10-12") == {10, 11, 12}

def test_parse_page_spec_mixed():
    assert parse_page_spec("1,3-5,7") == {1, 3, 4, 5, 7}

def test_parse_page_spec_invalid():
    with pytest.raises(ValueError):
        parse_page_spec("0")
    with pytest.raises(ValueError):
        parse_page_spec("a")
    with pytest.raises(ValueError):
        parse_page_spec("5-1")

def test_expand_article_paths(tmp_path):
    # Create dummy files
    f1 = tmp_path / "test1.pdf"
    f1.touch()
    f2 = tmp_path / "test2.md"
    f2.touch()
    
    # Test single path
    assert expand_article_paths([str(f1)]) == [f1]
    
    # Test glob
    pattern = str(tmp_path / "*.pdf")
    assert expand_article_paths([pattern]) == [f1]
    
    # Test multiple
    assert set(expand_article_paths([str(f1), str(f2)])) == {f1, f2}

def test_expand_article_paths_invalid(tmp_path):
    f = tmp_path / "test.txt"
    f.touch()
    with pytest.raises(click.UsageError):
        expand_article_paths([str(f)])
    with pytest.raises(click.UsageError):
        expand_article_paths(["nonexistent.pdf"])
