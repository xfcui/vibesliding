"""Expand a deck plan into a full script, one text call per slide."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.core.api_client import OpenRouterClient
from src.core.validate import PAGE_NUMBER_PATTERN, SLIDE_HEADER_PATTERN, strip_code_fences
from src.plan.parse import PlanDocument, PlanSlide
from src.write.prompts import CONTENT_ROLES, build_system_prompt, build_user_prompt

VISUAL_PATTERN = re.compile(r"\[Visual\s*:\s*(.*?)\]", re.IGNORECASE | re.DOTALL)
SPEECH_PATTERN = re.compile(r"\[Speech\s*:\s*(.*?)\]", re.IGNORECASE | re.DOTALL)
STYLE_PATTERN = re.compile(r"\[Styles?\s*:\s*.*?\]", re.IGNORECASE | re.DOTALL)
REFERENCE_PATTERN = re.compile(
    r"\[(?:Reference(?:\s+(?:Images?|Photos?))?|Refs?)\s*:.*?\]",
    re.IGNORECASE | re.DOTALL,
)
BULLET_PATTERN = re.compile(r"^[-*]\s+\S", re.MULTILINE)
BULLET_RANGES = {
    "hook": (6, 6),
    "content": (6, 6),
    "cta": (6, 6),
    "transition": (4, 4),
    "cover": (3, 4),
    "ending": (3, 4),
}


@dataclass(frozen=True)
class SlideDraft:
    """One assembled slide, successful or marked failed."""

    index: int
    title: str
    body: str
    failed: bool
    reasons: tuple[str, ...] = ()


def _extract_tag(pattern: re.Pattern[str], text: str) -> tuple[str, str]:
    matches = list(pattern.finditer(text))
    if not matches:
        return text, ""
    chosen = matches[-1]
    value = chosen.group(1).strip()
    stripped = text[: chosen.start()] + text[chosen.end() :]
    return stripped.strip(), value


def check_slide_body(text: str, slide: PlanSlide) -> list[str]:
    """Return reasons the model body fails the script shape. Empty means it passes."""
    reasons: list[str] = []
    cleaned = STYLE_PATTERN.sub("", REFERENCE_PATTERN.sub("", text))
    visuals = list(VISUAL_PATTERN.finditer(cleaned))
    speeches = list(SPEECH_PATTERN.finditer(cleaned))
    without_visual, visual = _extract_tag(VISUAL_PATTERN, cleaned)
    without_speech, _speech = _extract_tag(SPEECH_PATTERN, without_visual)
    bullets = BULLET_PATTERN.findall(without_speech)
    role = slide.role or "content"
    low, high = BULLET_RANGES.get(role, (3, 4))
    if not low <= len(bullets) <= high:
        expected = f"exactly {low}" if low == high else f"{low}-{high}"
        reasons.append(f"{len(bullets)} bullets, expected {expected}")
    if len(visuals) != 1:
        reasons.append(f"{len(visuals)} [Visual:] tags, expected exactly 1")
    if len(speeches) != 1:
        reasons.append(f"{len(speeches)} [Speech:] tags, expected exactly 1")
    if visual and len(visuals) == 1:
        marks = list(PAGE_NUMBER_PATTERN.finditer(visual))
        if role in CONTENT_ROLES:
            if not marks or any(
                mark.group(1) != str(slide.index) or mark.group(2) for mark in marks
            ):
                reasons.append(
                    f"expected 'Slide number: {slide.index}' without a page total in [Visual:]"
                )
        elif marks:
            reasons.append(f"{role} slide should not show a slide number")
    return reasons


def _canonical_body(text: str, slide: PlanSlide) -> str:
    """Reorder a passing model body: bullets, plan tags, visual, speech."""
    cleaned = STYLE_PATTERN.sub("", REFERENCE_PATTERN.sub("", strip_code_fences(text)))
    without_visual, visual = _extract_tag(VISUAL_PATTERN, cleaned)
    without_speech, speech = _extract_tag(SPEECH_PATTERN, without_visual)
    bullets = [
        line.strip()
        for line in without_speech.splitlines()
        if BULLET_PATTERN.match(line.strip())
    ]
    parts = list(bullets)
    if slide.style_tag:
        parts.append(slide.style_tag)
    if slide.reference_tag:
        parts.append(slide.reference_tag)
    if visual:
        parts.append(f"[Visual: {visual}]")
    if speech:
        parts.append(f"[Speech: {speech}]")
    return "\n".join(parts)


def _failed_body(slide: PlanSlide, reasons: list[str]) -> str:
    marker = f"<!-- write failed: {'; '.join(reasons)} -->"
    return f"{marker}\n{slide.body}".strip()


def assemble_script(document: PlanDocument, drafts: list[SlideDraft]) -> str:
    """Join slide drafts with the plan title and appendix."""
    title = document.title or "Untitled"
    chunks = [f"# PPT Outline: {title}", ""]
    for draft in drafts:
        chunks.append("---")
        chunks.append("")
        chunks.append(f"## Slide {draft.index}: {draft.title}")
        chunks.append(draft.body)
        chunks.append("")
    if document.appendix:
        chunks.append("---")
        chunks.append("")
        chunks.append(document.appendix.strip())
        chunks.append("")
    return "\n".join(chunks).rstrip() + "\n"


def merge_script(existing: str, drafts: list[SlideDraft], document: PlanDocument) -> str:
    """Replace selected slides inside an existing script; keep the rest."""
    by_index = {draft.index: draft for draft in drafts}
    appendix_at = existing.find("\n## Appendix")
    if appendix_at == -1 and existing.startswith("## Appendix"):
        appendix_at = 0
    script_end = appendix_at if appendix_at != -1 else len(existing)
    kept_appendix = existing[script_end:].strip() if appendix_at != -1 else ""
    headers = list(SLIDE_HEADER_PATTERN.finditer(existing[:script_end]))
    if not headers:
        return assemble_script(document, drafts)

    pieces: list[str] = [existing[: headers[0].start()].rstrip(), ""]
    for position, match in enumerate(headers):
        start = match.start()
        end = headers[position + 1].start() if position + 1 < len(headers) else script_end
        block = existing[start:end].strip()
        index = position + 1
        draft = by_index.get(index)
        if draft is None:
            pieces.append(block)
        else:
            pieces.append(f"## Slide {draft.index}: {draft.title}\n{draft.body}")
        pieces.append("")
    text = "\n".join(pieces).rstrip()
    appendix = kept_appendix or document.appendix.strip()
    if appendix:
        if not text.endswith("---"):
            text += "\n\n---"
        text += "\n\n" + appendix.strip()
    return text + "\n"


def save_write_prompt(directory: Path, index: int, system_prompt: str, user_prompt: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"slide_p{index:02d}_prompt.txt"
    path.write_text(
        f"## System prompt\n{system_prompt.strip()}\n\n## User prompt\n{user_prompt.strip()}\n",
        encoding="utf-8",
    )
    return path


async def write_script(
    client: OpenRouterClient,
    document: PlanDocument,
    *,
    idea: str,
    facts: str,
    standards: str,
    prompt_dir: Path,
    text_model: str | None = None,
    page_filter: set[int] | None = None,
    existing_script: str | None = None,
) -> tuple[str, list[SlideDraft]]:
    """Call the text model once per selected slide and assemble ``script`` markdown."""
    selected = [
        slide
        for slide in document.slides
        if page_filter is None or slide.index in page_filter
    ]
    if not selected:
        raise ValueError("No plan slides match the page filter.")
    if page_filter is not None and not (existing_script and existing_script.strip()):
        raise ValueError("Page filter requires an existing script to merge into.")

    prompts: list[tuple[str, str]] = []
    for slide in selected:
        system_prompt = build_system_prompt(standards, slide)
        user_prompt = build_user_prompt(document, slide, idea=idea, facts=facts)
        save_write_prompt(prompt_dir, slide.index, system_prompt, user_prompt)
        prompts.append((user_prompt, system_prompt))

    results = await client.complete_text_parallel(
        prompts,
        model=text_model,
        desc="Slide scripts",
    )

    drafts: list[SlideDraft] = []
    for slide, result in zip(selected, results):
        if isinstance(result, Exception):
            reasons = [str(result)]
            drafts.append(
                SlideDraft(
                    slide.index,
                    slide.title,
                    _failed_body(slide, reasons),
                    True,
                    tuple(reasons),
                )
            )
            continue
        body = strip_code_fences(result)
        reasons = check_slide_body(body, slide)
        if reasons:
            drafts.append(
                SlideDraft(
                    slide.index,
                    slide.title,
                    _failed_body(slide, reasons),
                    True,
                    tuple(reasons),
                )
            )
        else:
            drafts.append(
                SlideDraft(slide.index, slide.title, _canonical_body(body, slide), False)
            )

    if existing_script and page_filter is not None:
        script = merge_script(existing_script, drafts, document)
    else:
        script = assemble_script(document, drafts)
    return script, drafts
