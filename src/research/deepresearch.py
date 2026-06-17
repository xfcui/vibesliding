"""Valyu DeepResearch wrapper for idea-to-outline."""

from __future__ import annotations

import json
import logging
import time
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Final

from tqdm import tqdm

from src.core.config import DeepResearchMode

# macOS Command Line Tools Python 3.9 uses LibreSSL; urllib3 v2 warns on import.
warnings.filterwarnings(
    "ignore",
    message="urllib3 v2 only supports OpenSSL",
)

logger = logging.getLogger(__name__)

MODE_POLL_SETTINGS: Final[dict[DeepResearchMode, tuple[int, int]]] = {
    "fast": (5, 600),
    "standard": (10, 1800),
    "heavy": (30, 7200),
    "max": (60, 10800),
}

DEFAULT_REPORT_FORMAT: Final[str] = (
    "Structured research report optimized for presentation outline generation. "
    "Requirements: "
    "(1) Organize into clear thematic sections with H2 headers matching likely slide topics. "
    "(2) Lead each section with a concrete insight or claim, then support with specific facts, "
    "numbers, named examples, and quotable comparisons. "
    "(3) Attribute key claims to sources inline (author/org, year, or URL). "
    "(4) Include at least one real-world case study, named tool/product, or quantitative result "
    "per major section — the outline writer needs concrete anchors, not abstract summaries. "
    "(5) End each section with a one-sentence takeaway suitable for a slide's 'Core insight' bullet. "
    "(6) Prefer depth on fewer subtopics over shallow coverage of many. "
    "(7) Prioritize recent data (last 2 years) and note when older data is the best available. "
    "(8) Include before/after comparisons, performance deltas, or adoption metrics where available "
    "— these make strong visual slide content."
)

STATUS_RETRY_WAIT_INITIAL: Final[float] = 2.0
STATUS_RETRY_WAIT_MAX: Final[float] = 60.0

_TRANSIENT_ERROR_MARKERS: Final[tuple[str, ...]] = (
    "connection reset",
    "connection aborted",
    "connection error",
    "connection refused",
    "timed out",
    "timeout",
    "temporary failure",
    "network",
    "reset by peer",
    "broken pipe",
    "eof occurred",
    "name or service not known",
    "nodename nor servname",
    "ssl",
    "502",
    "503",
    "504",
    "429",
)

ProgressCallback = Callable[[Any], None]
StatusRetryCallback = Callable[[str, int, float], None]

_STATUS_LABELS: Final[dict[str, str]] = {
    "queued": "Queued",
    "running": "Researching",
    "awaiting_input": "Awaiting your input",
    "paused": "Paused",
    "completed": "Completed",
    "failed": "Failed",
    "cancelled": "Cancelled",
}


@dataclass(frozen=True)
class ResearchResult:
    """Completed DeepResearch output."""

    report: str
    sources: list[Any]
    cost: float
    task_id: str


@dataclass(frozen=True)
class ResearchState:
    """Persisted in-progress DeepResearch task metadata for resume."""

    task_id: str
    mode: DeepResearchMode

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2) + "\n"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchState:
        mode = data.get("mode", "standard")
        if mode not in MODE_POLL_SETTINGS:
            raise ValueError(f"Invalid research mode in state file: {mode!r}")
        task_id = data.get("task_id")
        if not task_id or not isinstance(task_id, str):
            raise ValueError("Research state file is missing task_id")
        return cls(task_id=task_id, mode=mode)  # type: ignore[arg-type]


def save_research_state(path: Path, state: ResearchState) -> None:
    """Write in-progress task metadata so polling can resume after interruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(state.to_json(), encoding="utf-8")


def load_research_state(path: Path) -> ResearchState:
    """Load persisted task metadata; raise ValueError if missing or invalid."""
    if not path.is_file():
        raise ValueError(f"Research state file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid research state file: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Invalid research state file: {path}")
    return ResearchState.from_dict(data)


def clear_research_state(path: Path) -> None:
    """Remove persisted task metadata after a successful run."""
    if path.is_file():
        path.unlink()


def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _status_value(status: Any) -> str:
    raw = _get_attr(status, "status", "unknown")
    if hasattr(raw, "value"):
        return str(raw.value)
    return str(raw)


def _status_label(status: Any) -> str:
    return _STATUS_LABELS.get(_status_value(status), _status_value(status))


def _latest_message(messages: Any) -> str | None:
    if not messages:
        return None
    last = messages[-1]
    if isinstance(last, str):
        text = last.strip()
        return text[:140] if text else None
    if isinstance(last, dict):
        for key in ("content", "text", "message", "summary"):
            val = last.get(key)
            if val:
                return str(val).strip()[:140]
    content = _get_attr(last, "content")
    if isinstance(content, str) and content.strip():
        return content.strip()[:140]
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if text:
                    return str(text).strip()[:140]
    return None


def _progress_key(status: Any) -> tuple[Any, ...]:
    progress = _get_attr(status, "progress")
    current = _get_attr(progress, "current_step")
    total = _get_attr(progress, "total_steps")
    sources = _get_attr(status, "sources") or []
    messages = _get_attr(status, "messages") or []
    interaction = _get_attr(status, "interaction")
    interaction_type = _get_attr(interaction, "type")
    if hasattr(interaction_type, "value"):
        interaction_type = interaction_type.value
    return (
        _status_value(status),
        current,
        total,
        len(sources),
        len(messages),
        _latest_message(messages),
        _get_attr(status, "title"),
        interaction_type,
        _get_attr(status, "cost"),
    )


def format_progress(
    status: Any,
    *,
    elapsed_s: float | None = None,
) -> str:
    """Format a Valyu DeepResearch status update for CLI display."""
    parts: list[str] = [_status_label(status)]

    progress = _get_attr(status, "progress")
    if progress is not None:
        current = _get_attr(progress, "current_step")
        total = _get_attr(progress, "total_steps")
        if current is not None and total:
            pct = (current / total) * 100
            parts.append(f"step {current}/{total} ({pct:.0f}%)")

    sources = _get_attr(status, "sources")
    if sources:
        parts.append(f"{len(sources)} sources found")

    cost = _get_attr(status, "cost")
    if cost is not None:
        parts.append(f"cost ${float(cost):.2f}")

    title = _get_attr(status, "title")
    if title:
        parts.append(f'"{str(title).strip()[:80]}"')

    interaction = _get_attr(status, "interaction")
    if interaction is not None:
        itype = _get_attr(interaction, "type")
        if hasattr(itype, "value"):
            itype = itype.value
        if itype:
            parts.append(f"checkpoint: {str(itype).replace('_', ' ')}")

    message = _latest_message(_get_attr(status, "messages"))
    if message:
        parts.append(message)

    if elapsed_s is not None:
        elapsed = int(elapsed_s)
        mins, secs = divmod(elapsed, 60)
        if mins:
            parts.append(f"{mins}m {secs:02d}s elapsed")
        else:
            parts.append(f"{secs}s elapsed")

    return " · ".join(parts)


class TqdmProgressReporter:
    """tqdm-based progress reporter for long-running DeepResearch polls."""

    def __init__(self, *, heartbeat_s: float = 30.0) -> None:
        self._heartbeat_s = heartbeat_s
        self._pbar = tqdm(desc="DeepResearch", unit="poll", dynamic_ncols=True)
        self._last_key: tuple[Any, ...] | None = None
        self._last_print = time.monotonic()
        self._start = time.monotonic()

    def __call__(self, status: Any) -> None:
        key = _progress_key(status)
        now = time.monotonic()
        elapsed = now - self._start
        if key != self._last_key or now - self._last_print >= self._heartbeat_s:
            self._last_key = key
            self._last_print = now
            self._pbar.set_postfix_str(
                format_progress(status, elapsed_s=elapsed),
                refresh=False,
            )
            self._pbar.update(1)

    def close(self) -> None:
        self._pbar.close()


def make_progress_printer(
    on_line: Callable[[str], None],
    *,
    heartbeat_s: float = 30.0,
) -> ProgressCallback:
    """Return a callback that prints only when progress meaningfully changes.

    Emits a heartbeat line every *heartbeat_s* seconds so long runs still feel alive.
    """
    last_key: tuple[Any, ...] | None = None
    last_print = time.monotonic()
    start = time.monotonic()

    def callback(status: Any) -> None:
        nonlocal last_key, last_print
        key = _progress_key(status)
        now = time.monotonic()
        elapsed = now - start
        if key != last_key or now - last_print >= heartbeat_s:
            last_key = key
            last_print = now
            on_line(format_progress(status, elapsed_s=elapsed))

    return callback


def _is_transient_status_error(error: Any) -> bool:
    """Return True when a status poll failure is likely a transient network issue."""
    if error is None:
        return False
    if isinstance(error, tuple):
        for item in error:
            if isinstance(
                item,
                (ConnectionResetError, ConnectionError, TimeoutError, OSError),
            ):
                return True
    if isinstance(
        error,
        (ConnectionResetError, ConnectionError, TimeoutError, OSError),
    ):
        return True
    text = str(error).lower()
    return any(marker in text for marker in _TRANSIENT_ERROR_MARKERS)


def _fetch_status_resilient(
    deepresearch: Any,
    task_id: str,
    *,
    on_status_retry: StatusRetryCallback | None = None,
) -> Any:
    """Poll task status, retrying transient network failures until one succeeds."""
    wait_s = STATUS_RETRY_WAIT_INITIAL
    attempt = 0
    while True:
        status = deepresearch.status(task_id)
        if status.success or not _is_transient_status_error(status.error):
            return status
        attempt += 1
        logger.warning(
            "DeepResearch status poll failed (attempt %d): %s; retrying in %.1fs",
            attempt,
            status.error,
            wait_s,
        )
        if on_status_retry is not None:
            on_status_retry(str(status.error), attempt, wait_s)
        time.sleep(wait_s)
        wait_s = min(wait_s * 2, STATUS_RETRY_WAIT_MAX)


def _wait_for_deepresearch(
    deepresearch: Any,
    task_id: str,
    *,
    poll_interval: int,
    max_wait_time: int,
    on_progress: ProgressCallback | None = None,
    on_status_retry: StatusRetryCallback | None = None,
) -> Any:
    """Poll until the DeepResearch task reaches a terminal state.

    Unlike Valyu's built-in ``wait``, transient status-poll network errors are
    retried with exponential backoff instead of aborting the whole run.
    """
    start_time = time.monotonic()

    while True:
        status = _fetch_status_resilient(
            deepresearch,
            task_id,
            on_status_retry=on_status_retry,
        )
        if not status.success:
            raise ValueError(f"Failed to get status: {status.error}")

        if on_progress is not None:
            on_progress(status)

        task_status = _status_value(status)
        if task_status == "completed":
            return status
        if task_status == "failed":
            error = _get_attr(status, "error") or task_status
            raise ValueError(f"Task failed: {error}")
        if task_status == "cancelled":
            raise ValueError("Task was cancelled")

        elapsed = time.monotonic() - start_time
        if elapsed > max_wait_time:
            raise TimeoutError(
                f"Task did not complete within {max_wait_time} seconds"
            )

        time.sleep(poll_interval)


def resolve_datasource_ids(valyu: Any, categories: tuple[str, ...]) -> list[str]:
    """Resolve Valyu datasource category IDs to concrete datasource IDs."""
    if not categories:
        return []

    ids: list[str] = []
    seen: set[str] = set()
    for category in categories:
        response = valyu.datasources(category=category)
        success = _get_attr(response, "success", False)
        if not success:
            error = _get_attr(response, "error", "unknown error")
            raise RuntimeError(
                f"Failed to list Valyu datasources for category {category!r}: {error}"
            )
        for ds in _get_attr(response, "datasources", []) or []:
            ds_id = _get_attr(ds, "id")
            if ds_id and ds_id not in seen:
                seen.add(ds_id)
                ids.append(ds_id)
    return ids


def _get_valyu_client(api_key: str) -> Any:
    try:
        from valyu import Valyu
    except ImportError as exc:
        raise ImportError(
            "valyu package is required for outline generation. "
            "Install with: pip install valyu"
        ) from exc
    return Valyu(api_key)


def _build_create_kwargs(
    valyu: Any,
    idea: str,
    *,
    mode: DeepResearchMode,
    categories: tuple[str, ...],
    report_format: str | None,
) -> dict[str, Any]:
    create_kwargs: dict[str, Any] = {
        "query": idea,
        "mode": mode,
        "output_formats": ["markdown"],
        "report_format": report_format or DEFAULT_REPORT_FORMAT,
    }
    if categories:
        included_sources = resolve_datasource_ids(valyu, categories)
        if not included_sources:
            raise RuntimeError(
                f"No Valyu datasources found for categories: {', '.join(categories)}"
            )
        create_kwargs["search"] = {
            "search_type": "proprietary",
            "included_sources": included_sources,
        }
    return create_kwargs


def _create_deepresearch_resilient(
    valyu: Any,
    create_kwargs: dict[str, Any],
    *,
    on_status_retry: StatusRetryCallback | None = None,
) -> str:
    """Create a DeepResearch task, retrying transient network failures until one succeeds."""
    wait_s = STATUS_RETRY_WAIT_INITIAL
    attempt = 0
    while True:
        try:
            task = valyu.deepresearch.create(**create_kwargs)
        except Exception as exc:
            if not _is_transient_status_error(exc):
                raise
            attempt += 1
            logger.warning(
                "DeepResearch task creation failed (attempt %d): %s; retrying in %.1fs",
                attempt,
                exc,
                wait_s,
            )
            if on_status_retry is not None:
                on_status_retry(str(exc), attempt, wait_s)
            time.sleep(wait_s)
            wait_s = min(wait_s * 2, STATUS_RETRY_WAIT_MAX)
            continue

        if getattr(task, "success", True):
            task_id = task.deepresearch_id
            if not task_id:
                raise RuntimeError(
                    "DeepResearch create succeeded but returned no task ID"
                )
            return task_id

        error_msg = getattr(task, "error", "unknown error")
        if _is_transient_status_error(error_msg):
            attempt += 1
            logger.warning(
                "DeepResearch task creation failed (attempt %d): %s; retrying in %.1fs",
                attempt,
                error_msg,
                wait_s,
            )
            if on_status_retry is not None:
                on_status_retry(str(error_msg), attempt, wait_s)
            time.sleep(wait_s)
            wait_s = min(wait_s * 2, STATUS_RETRY_WAIT_MAX)
            continue

        raise RuntimeError(f"Failed to create DeepResearch task: {error_msg}")


def create_deepresearch_task(
    idea: str,
    *,
    api_key: str,
    mode: DeepResearchMode = "standard",
    categories: tuple[str, ...] = (),
    report_format: str | None = None,
    on_status_retry: StatusRetryCallback | None = None,
) -> str:
    """Start a Valyu DeepResearch task and return its task ID."""
    valyu = _get_valyu_client(api_key)
    create_kwargs = _build_create_kwargs(
        valyu,
        idea,
        mode=mode,
        categories=categories,
        report_format=report_format,
    )
    return _create_deepresearch_resilient(
        valyu,
        create_kwargs,
        on_status_retry=on_status_retry,
    )


def _result_from_status(status: Any, task_id: str) -> ResearchResult:
    output = status.output
    if not isinstance(output, str) or not output.strip():
        raise RuntimeError("DeepResearch completed but returned empty output")

    sources = list(getattr(status, "sources", None) or [])
    cost = float(getattr(status, "cost", 0.0) or 0.0)
    resolved_task_id = getattr(status, "deepresearch_id", None) or task_id

    return ResearchResult(
        report=output,
        sources=sources,
        cost=cost,
        task_id=resolved_task_id,
    )


def wait_for_deepresearch_result(
    task_id: str,
    *,
    api_key: str,
    mode: DeepResearchMode = "standard",
    on_progress: ProgressCallback | None = None,
    on_status_retry: StatusRetryCallback | None = None,
) -> ResearchResult:
    """Poll an existing DeepResearch task until it completes."""
    valyu = _get_valyu_client(api_key)
    poll_interval, max_wait_time = MODE_POLL_SETTINGS[mode]
    status = _wait_for_deepresearch(
        valyu.deepresearch,
        task_id,
        poll_interval=poll_interval,
        max_wait_time=max_wait_time,
        on_progress=on_progress,
        on_status_retry=on_status_retry,
    )
    return _result_from_status(status, task_id)


def resume_deepresearch(
    task_id: str,
    *,
    api_key: str,
    mode: DeepResearchMode = "standard",
    on_progress: ProgressCallback | None = None,
    on_status_retry: StatusRetryCallback | None = None,
    state_path: Path | None = None,
) -> ResearchResult:
    """Resume polling a previously started DeepResearch task."""
    try:
        result = wait_for_deepresearch_result(
            task_id,
            api_key=api_key,
            mode=mode,
            on_progress=on_progress,
            on_status_retry=on_status_retry,
        )
    except (ValueError, TimeoutError):
        if state_path is not None:
            clear_research_state(state_path)
        raise

    if state_path is not None:
        clear_research_state(state_path)
    return result


def run_deepresearch(
    idea: str,
    *,
    api_key: str,
    mode: DeepResearchMode = "standard",
    categories: tuple[str, ...] = (),
    report_format: str | None = None,
    on_progress: ProgressCallback | None = None,
    on_status_retry: StatusRetryCallback | None = None,
    state_path: Path | None = None,
) -> ResearchResult:
    """Run Valyu DeepResearch and return the markdown report.

    Args:
        idea: Research query / presentation topic seed.
        api_key: Valyu API key.
        mode: DeepResearch mode (fast, standard, heavy, max).
        categories: Optional Valyu datasource categories to restrict search to.
        report_format: Optional natural-language output instructions.
        on_progress: Optional callback invoked on each poll with status object.
        state_path: Optional path to persist task metadata for resume.

    Returns:
        ResearchResult with markdown report, sources, and cost.

    Raises:
        RuntimeError: If the task does not complete successfully.
        ImportError: If the valyu package is not installed.
    """
    task_id = create_deepresearch_task(
        idea,
        api_key=api_key,
        mode=mode,
        categories=categories,
        report_format=report_format,
        on_status_retry=on_status_retry,
    )
    if state_path is not None:
        save_research_state(state_path, ResearchState(task_id=task_id, mode=mode))

    try:
        result = wait_for_deepresearch_result(
            task_id,
            api_key=api_key,
            mode=mode,
            on_progress=on_progress,
            on_status_retry=on_status_retry,
        )
    except (ValueError, TimeoutError):
        raise

    if state_path is not None:
        clear_research_state(state_path)
    return result
