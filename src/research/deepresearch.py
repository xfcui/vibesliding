"""Valyu DeepResearch wrapper for idea-to-outline."""

from __future__ import annotations

import logging
import time
import warnings
from dataclasses import dataclass
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


def run_deepresearch(
    idea: str,
    *,
    api_key: str,
    mode: DeepResearchMode = "standard",
    categories: tuple[str, ...] = (),
    report_format: str | None = None,
    on_progress: ProgressCallback | None = None,
    on_status_retry: StatusRetryCallback | None = None,
) -> ResearchResult:
    """Run Valyu DeepResearch and return the markdown report.

    Args:
        idea: Research query / presentation topic seed.
        api_key: Valyu API key.
        mode: DeepResearch mode (fast, standard, heavy, max).
        categories: Optional Valyu datasource categories to restrict search to.
        report_format: Optional natural-language output instructions.
        on_progress: Optional callback invoked on each poll with status object.

    Returns:
        ResearchResult with markdown report, sources, and cost.

    Raises:
        RuntimeError: If the task does not complete successfully.
        ImportError: If the valyu package is not installed.
    """
    try:
        from valyu import Valyu
    except ImportError as exc:
        raise ImportError(
            "valyu package is required for outline generation. "
            "Install with: pip install valyu"
        ) from exc

    poll_interval, max_wait_time = MODE_POLL_SETTINGS[mode]
    valyu = Valyu(api_key)

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

    task = valyu.deepresearch.create(**create_kwargs)

    result = _wait_for_deepresearch(
        valyu.deepresearch,
        task.deepresearch_id,
        poll_interval=poll_interval,
        max_wait_time=max_wait_time,
        on_progress=on_progress,
        on_status_retry=on_status_retry,
    )

    output = result.output
    if not isinstance(output, str) or not output.strip():
        raise RuntimeError("DeepResearch completed but returned empty output")

    sources = list(getattr(result, "sources", None) or [])
    cost = float(getattr(result, "cost", 0.0) or 0.0)
    task_id = getattr(result, "deepresearch_id", None) or task.deepresearch_id

    return ResearchResult(
        report=output,
        sources=sources,
        cost=cost,
        task_id=task_id,
    )


def format_sources_for_prompt(sources: list[Any], *, max_sources: int = 20) -> str:
    """Format DeepResearch sources as a compact bibliography for the outline LLM."""
    if not sources:
        return "(No sources returned)"

    lines: list[str] = []
    for index, source in enumerate(sources[:max_sources], start=1):
        title = getattr(source, "title", None) or "Untitled"
        url = getattr(source, "url", None) or ""
        snippet = getattr(source, "snippet", None) or ""
        if snippet and len(snippet) > 200:
            snippet = snippet[:200] + "..."
        line = f"{index}. {title}"
        if url:
            line += f" — {url}"
        if snippet:
            line += f"\n   {snippet}"
        lines.append(line)

    if len(sources) > max_sources:
        lines.append(f"... and {len(sources) - max_sources} more sources")

    return "\n".join(lines)
