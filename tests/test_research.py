"""Tests for Valyu DeepResearch wrapper."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.research import (
    make_progress_printer,
    run_deepresearch,
)
from src.research.deepresearch import (
    MODE_POLL_SETTINGS,
    ResearchState,
    _create_deepresearch_resilient,
    _fetch_status_resilient,
    _is_transient_status_error,
    clear_research_state,
    create_deepresearch_task,
    format_progress,
    load_research_state,
    resolve_datasource_ids,
    resume_deepresearch,
    run_deepresearch,
    save_research_state,
    wait_for_deepresearch_result,
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

    def test_saves_and_clears_state_on_success(self, tmp_path: Path) -> None:
        state_path = tmp_path / "research_state.json"
        mock_task = SimpleNamespace(deepresearch_id="dr_state")
        mock_result = SimpleNamespace(
            success=True,
            status="completed",
            output="# Report",
            sources=[],
            cost=0.5,
            deepresearch_id="dr_state",
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
            run_deepresearch(
                "topic",
                api_key="key",
                state_path=state_path,
            )

        assert not state_path.is_file()

    def test_resume_polls_existing_task(self) -> None:
        mock_result = SimpleNamespace(
            success=True,
            status="completed",
            output="# Resumed Report",
            sources=[],
            cost=0.25,
            deepresearch_id="dr_resume",
            error=None,
        )

        mock_deepresearch = MagicMock()
        mock_deepresearch.status.return_value = mock_result

        mock_valyu = MagicMock()
        mock_valyu.deepresearch = mock_deepresearch

        with (
            patch("valyu.Valyu", return_value=mock_valyu),
            patch("src.research.deepresearch.time.sleep"),
        ):
            result = resume_deepresearch(
                "dr_resume",
                api_key="key",
                mode="fast",
            )

        assert result.report == "# Resumed Report"
        mock_deepresearch.create.assert_not_called()
        mock_deepresearch.status.assert_called()


class TestResearchState:
    def test_round_trip_json(self, tmp_path: Path) -> None:
        state_path = tmp_path / "research_state.json"
        original = ResearchState(task_id="dr_abc", mode="heavy")
        save_research_state(state_path, original)
        loaded = load_research_state(state_path)
        assert loaded == original

    def test_clear_removes_file(self, tmp_path: Path) -> None:
        state_path = tmp_path / "research_state.json"
        save_research_state(state_path, ResearchState(task_id="dr_x", mode="fast"))
        clear_research_state(state_path)
        assert not state_path.is_file()

    def test_resume_clears_state_on_terminal_failure(self, tmp_path: Path) -> None:
        state_path = tmp_path / "research_state.json"
        save_research_state(state_path, ResearchState(task_id="dr_fail", mode="fast"))

        mock_result = SimpleNamespace(
            success=True,
            status="failed",
            output="",
            sources=[],
            cost=0.0,
            error="timeout",
        )
        mock_deepresearch = MagicMock()
        mock_deepresearch.status.return_value = mock_result
        mock_valyu = MagicMock()
        mock_valyu.deepresearch = mock_deepresearch

        with (
            patch("valyu.Valyu", return_value=mock_valyu),
            patch("src.research.deepresearch.time.sleep"),
            pytest.raises(ValueError, match="Task failed"),
        ):
            resume_deepresearch(
                "dr_fail",
                api_key="key",
                mode="fast",
                state_path=state_path,
            )

        assert not state_path.is_file()


class TestCreateRetries:
    def test_create_retries_transient_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        sleeps: list[float] = []
        monkeypatch.setattr("src.research.deepresearch.time.sleep", lambda s: sleeps.append(s))

        transient = SimpleNamespace(
            success=False,
            error=("Connection aborted.", ConnectionResetError(54, "Connection reset by peer")),
            deepresearch_id=None,
        )
        created = SimpleNamespace(success=True, deepresearch_id="dr_retry", error=None)
        mock_deepresearch = MagicMock()
        mock_deepresearch.create.side_effect = [transient, created]
        mock_valyu = MagicMock()
        mock_valyu.deepresearch = mock_deepresearch

        task_id = _create_deepresearch_resilient(
            mock_valyu,
            {"query": "topic", "mode": "standard", "output_formats": ["markdown"]},
        )

        assert task_id == "dr_retry"
        assert mock_deepresearch.create.call_count == 2
        assert sleeps == [2.0]

    def test_billing_error_raises(self) -> None:
        mock_task = SimpleNamespace(
            success=False,
            error="Monthly credit limit exceeded. Please increase your limits.",
            deepresearch_id=None,
        )
        mock_valyu = MagicMock()
        mock_valyu.deepresearch.create.return_value = mock_task

        with patch("valyu.Valyu", return_value=mock_valyu):
            with pytest.raises(RuntimeError, match="Failed to create DeepResearch task"):
                create_deepresearch_task("AI agents in software", api_key="key")
