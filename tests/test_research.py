"""Tests for Valyu DeepResearch wrapper."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.research import (
    format_sources_for_prompt,
    make_progress_printer,
    run_deepresearch,
)
from src.research.deepresearch import (
    MODE_POLL_SETTINGS,
    _fetch_status_resilient,
    _is_transient_status_error,
    format_progress,
    resolve_datasource_ids,
)


class TestFormatProgress:
    def test_includes_status_and_percent(self) -> None:
        status = SimpleNamespace(
            status="running",
            progress=SimpleNamespace(current_step=3, total_steps=10),
            sources=[SimpleNamespace(title="A")],
            messages=[{"content": "Searching academic papers on Cursor IDE"}],
        )
        text = format_progress(status, elapsed_s=125)
        assert "Researching" in text
        assert "step 3/10 (30%)" in text
        assert "1 sources found" in text
        assert "Searching academic papers" in text
        assert "2m 05s elapsed" in text

    def test_deduplicates_unchanged_updates(self) -> None:
        lines: list[str] = []
        printer = make_progress_printer(lines.append, heartbeat_s=9999)
        status = SimpleNamespace(status="running", progress=None, messages=None, sources=[])
        printer(status)
        printer(status)
        assert len(lines) == 1
        assert "Researching" in lines[0]

    def test_prints_again_when_message_changes(self) -> None:
        lines: list[str] = []
        printer = make_progress_printer(lines.append, heartbeat_s=9999)
        printer(SimpleNamespace(status="running", messages=["Planning research"]))
        printer(SimpleNamespace(status="running", messages=["Planning research", "Gathering sources"]))
        assert len(lines) == 2
        assert "Gathering sources" in lines[1]


class TestFormatSources:
    def test_formats_source_list(self) -> None:
        sources = [
            SimpleNamespace(
                title="Paper A",
                url="https://example.com/a",
                snippet="Short snippet",
            )
        ]
        text = format_sources_for_prompt(sources)
        assert "Paper A" in text
        assert "https://example.com/a" in text
        assert "Short snippet" in text

    def test_empty_sources(self) -> None:
        assert "(No sources returned)" in format_sources_for_prompt([])


class TestTransientStatusErrors:
    def test_detects_connection_reset_tuple(self) -> None:
        error = ("Connection aborted.", ConnectionResetError(54, "Connection reset by peer"))
        assert _is_transient_status_error(error) is True

    def test_ignores_permanent_task_errors(self) -> None:
        assert _is_transient_status_error("Task not found") is False


class TestFetchStatusResilient:
    def test_retries_transient_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        sleeps: list[float] = []
        monkeypatch.setattr("src.research.deepresearch.time.sleep", lambda s: sleeps.append(s))

        transient = SimpleNamespace(
            success=False,
            error=("Connection aborted.", ConnectionResetError(54, "Connection reset by peer")),
        )
        completed = SimpleNamespace(success=True, status="completed", error=None)
        mock_deepresearch = MagicMock()
        mock_deepresearch.status.side_effect = [transient, transient, completed]

        result = _fetch_status_resilient(mock_deepresearch, "dr_retry")

        assert result is completed
        assert mock_deepresearch.status.call_count == 3
        assert sleeps == [2.0, 4.0]


class TestRunDeepresearch:
    def test_success_returns_report(self) -> None:
        mock_task = SimpleNamespace(deepresearch_id="dr_test_123")
        mock_result = SimpleNamespace(
            success=True,
            status="completed",
            output="# Research Report\n\nKey findings.",
            sources=[SimpleNamespace(title="S1", url="https://x.com", snippet="")],
            cost=1.25,
            deepresearch_id="dr_test_123",
            error=None,
        )

        mock_deepresearch = MagicMock()
        mock_deepresearch.create.return_value = mock_task
        mock_deepresearch.status.return_value = mock_result

        mock_valyu = MagicMock()
        mock_valyu.deepresearch = mock_deepresearch

        with (
            patch("valyu.Valyu", return_value=mock_valyu),
            patch("src.research.deepresearch.time.sleep"),
        ):
            result = run_deepresearch(
                "AI agents in software",
                api_key="valyu-key",
                mode="standard",
            )

        assert result.report.startswith("# Research Report")
        assert result.cost == 1.25
        assert result.task_id == "dr_test_123"
        assert len(result.sources) == 1

        mock_deepresearch.create.assert_called_once()
        create_kwargs = mock_deepresearch.create.call_args.kwargs
        assert create_kwargs["query"] == "AI agents in software"
        assert create_kwargs["mode"] == "standard"
        assert create_kwargs["output_formats"] == ["markdown"]
        assert "search" not in create_kwargs
        poll_interval, max_wait = MODE_POLL_SETTINGS["standard"]
        assert poll_interval == 10
        assert max_wait == 1800

    def test_categories_restrict_included_sources(self) -> None:
        mock_task = SimpleNamespace(deepresearch_id="dr_cat")
        mock_result = SimpleNamespace(
            success=True,
            status="completed",
            output="# Report",
            sources=[],
            cost=0.5,
            deepresearch_id="dr_cat",
            error=None,
        )

        mock_ds_response = SimpleNamespace(
            success=True,
            datasources=[
                SimpleNamespace(id="valyu/valyu-arxiv"),
                SimpleNamespace(id="valyu/valyu-pubmed"),
            ],
        )
        mock_valyu = MagicMock()
        mock_valyu.datasources.return_value = mock_ds_response

        mock_deepresearch = MagicMock()
        mock_deepresearch.create.return_value = mock_task
        mock_deepresearch.status.return_value = mock_result
        mock_valyu.deepresearch = mock_deepresearch

        with (
            patch("valyu.Valyu", return_value=mock_valyu),
            patch("src.research.deepresearch.time.sleep"),
        ):
            run_deepresearch(
                "topic",
                api_key="key",
                categories=("research",),
            )

        mock_valyu.datasources.assert_called_once_with(category="research")
        create_kwargs = mock_deepresearch.create.call_args.kwargs
        assert create_kwargs["search"] == {
            "search_type": "proprietary",
            "included_sources": ["valyu/valyu-arxiv", "valyu/valyu-pubmed"],
        }

    def test_failed_task_raises(self) -> None:
        mock_task = SimpleNamespace(deepresearch_id="dr_fail")
        mock_result = SimpleNamespace(
            success=True,
            status="failed",
            output="",
            sources=[],
            cost=0.0,
            error="timeout",
        )

        mock_deepresearch = MagicMock()
        mock_deepresearch.create.return_value = mock_task
        mock_deepresearch.status.return_value = mock_result

        mock_valyu = MagicMock()
        mock_valyu.deepresearch = mock_deepresearch

        with (
            patch("valyu.Valyu", return_value=mock_valyu),
            patch("src.research.deepresearch.time.sleep"),
        ):
            with pytest.raises(ValueError, match="Task failed"):
                run_deepresearch("topic", api_key="key")

    def test_empty_output_raises(self) -> None:
        mock_task = SimpleNamespace(deepresearch_id="dr_empty")
        mock_result = SimpleNamespace(
            success=True,
            status="completed",
            output="   ",
            sources=[],
            cost=0.0,
            error=None,
        )

        mock_deepresearch = MagicMock()
        mock_deepresearch.create.return_value = mock_task
        mock_deepresearch.status.return_value = mock_result

        mock_valyu = MagicMock()
        mock_valyu.deepresearch = mock_deepresearch

        with (
            patch("valyu.Valyu", return_value=mock_valyu),
            patch("src.research.deepresearch.time.sleep"),
        ):
            with pytest.raises(RuntimeError, match="empty output"):
                run_deepresearch("topic", api_key="key")

    def test_progress_callback_invoked(self) -> None:
        mock_task = SimpleNamespace(deepresearch_id="dr_cb")
        running = SimpleNamespace(success=True, status="running", error=None)
        completed = SimpleNamespace(
            success=True,
            status="completed",
            output="Report body",
            sources=[],
            cost=0.5,
            deepresearch_id="dr_cb",
            error=None,
        )

        mock_deepresearch = MagicMock()
        mock_deepresearch.create.return_value = mock_task
        mock_deepresearch.status.side_effect = [running, completed]

        mock_valyu = MagicMock()
        mock_valyu.deepresearch = mock_deepresearch

        seen: list[object] = []

        def on_progress(status: object) -> None:
            seen.append(status)

        with (
            patch("valyu.Valyu", return_value=mock_valyu),
            patch("src.research.deepresearch.time.sleep"),
        ):
            run_deepresearch("topic", api_key="key", on_progress=on_progress)

        assert len(seen) == 2
        assert seen[0] is running
        assert seen[1] is completed
