import httpx
import pytest
import click
from pathlib import Path
from click.testing import CliRunner

from src.api_client import OpenRouterClient
from src.cli import main, parse_page_spec, expand_article_paths, expand_style_paths

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


def test_expand_style_paths_glob_sorted(tmp_path):
    (tmp_path / "style_zebra.png").write_bytes(b"x")
    (tmp_path / "style_alpha.png").write_bytes(b"y")
    pattern = str(tmp_path / "style_*.png")
    got = expand_style_paths([pattern])
    assert [p.name for p in got] == ["style_alpha.png", "style_zebra.png"]


def test_expand_style_paths_duplicate_glob_same_file(tmp_path):
    p = tmp_path / "style_x.png"
    p.write_bytes(b"z")
    pat = str(tmp_path / "*.png")
    got = expand_style_paths([pat, pat])
    assert len(got) == 1 and got[0] == p


def test_expand_style_paths_invalid_extension(tmp_path):
    gif = tmp_path / "bad.gif"
    gif.write_bytes(b"g")
    with pytest.raises(click.UsageError, match="Unsupported style"):
        expand_style_paths([str(gif)])


def test_balance_only_prints_openrouter_credits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, respx_mock
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "max_concurrent = 1\nprovider = openrouter\n\n"
        "[openrouter]\napi_key = sk-t\nmodel = m\n",
        encoding="utf-8",
    )
    respx_mock.get(f"{OpenRouterClient.BASE_URL}/credits").mock(
        return_value=httpx.Response(
            200,
            json={"data": {"total_credits": 10.0, "total_usage": 2.0}},
        )
    )
    runner = CliRunner()
    result = runner.invoke(main, ["--balance-only"])
    assert result.exit_code == 0
    assert "OpenRouter credits" in result.output
    assert "8" in result.output


def test_balance_only_rejects_outline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "max_concurrent = 1\nprovider = openrouter\n\n"
        "[openrouter]\napi_key = sk-t\nmodel = m\n",
        encoding="utf-8",
    )
    outline = tmp_path / "o.md"
    outline.write_text("# x\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["--balance-only", "--outline", str(outline)])
    assert result.exit_code != 0


def test_balance_only_rejects_no_balance() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--balance-only", "--no-balance"])
    assert result.exit_code != 0


def test_missing_outline_shows_hint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "max_concurrent = 1\nprovider = openrouter\n\n"
        "[openrouter]\napi_key = sk-t\nmodel = m\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert "--outline" in result.output.lower() or "outline" in result.output.lower()
