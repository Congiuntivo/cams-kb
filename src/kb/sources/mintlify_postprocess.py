from __future__ import annotations

import re

import yaml

_CALLOUT_TAGS = ("Note", "Warning", "Info", "Tip", "Check")
_WRAPPER_TAGS = ("Steps", "Tabs", "Frame", "CardGroup", "AccordionGroup", "CodeGroup")

_ICON_PATTERN = re.compile(r"<Icon\s[^>]*/?>", re.DOTALL)
_CALLOUT_PATTERN = re.compile(
    r"<(" + "|".join(_CALLOUT_TAGS) + r")(?:\s[^>]*)?>(.+?)</\1>",
    re.DOTALL,
)
_WRAPPER_PATTERN = re.compile(
    r"<(" + "|".join(_WRAPPER_TAGS) + r")(?:\s[^>]*)?>(.+?)</\1>",
    re.DOTALL,
)
_STEP_PATTERN = re.compile(r"<Step(\s[^>]*)?>(.*?)</Step>", re.DOTALL)
_TAB_PATTERN = re.compile(r"<Tab(\s[^>]*)>(.*?)</Tab>", re.DOTALL)
_ACCORDION_PATTERN = re.compile(r"<Accordion(\s[^>]*)>(.*?)</Accordion>", re.DOTALL)
_CARD_PATTERN = re.compile(r"<Card(\s[^>]*)>(.*?)</Card>", re.DOTALL)

_MAX_PASSES = 20


def _extract_title(attrs: str | None) -> str:
    if not attrs:
        return ""
    match = re.search(r'title="([^"]*)"', attrs)
    return match.group(1) if match else ""


def _blockquote(label: str, content: str) -> str:
    lines = content.strip().split("\n")
    quoted = "\n".join(f"> {line}" if line.strip() else ">" for line in lines)
    return f"> **{label}:**\n{quoted}"


def _headed(marker: str, title: str, content: str) -> str:
    body = content.strip()
    if body:
        return f"{marker} {title}\n\n{body}"
    return f"{marker} {title}"


def _strip_icons(text: str) -> str:
    return _ICON_PATTERN.sub("", text)


def _transform_callouts(text: str) -> str:
    return _CALLOUT_PATTERN.sub(
        lambda m: _blockquote(m.group(1), m.group(2)),
        text,
    )


def _transform_steps(text: str) -> str:
    def replace(m: re.Match) -> str:
        title = _extract_title(m.group(1) or "")
        if title:
            return _headed("###", title, m.group(2))
        return m.group(2).strip()

    return _STEP_PATTERN.sub(replace, text)


def _transform_tabs(text: str) -> str:
    return _TAB_PATTERN.sub(
        lambda m: _headed("##", _extract_title(m.group(1)), m.group(2)),
        text,
    )


def _transform_accordions(text: str) -> str:
    return _ACCORDION_PATTERN.sub(
        lambda m: _headed("##", _extract_title(m.group(1)), m.group(2)),
        text,
    )


def _transform_cards(text: str) -> str:
    def replace(m: re.Match) -> str:
        title = _extract_title(m.group(1))
        content = m.group(2).strip()
        return f"**{title}**\n\n{content}" if content else f"**{title}**"

    return _CARD_PATTERN.sub(replace, text)


def _strip_wrappers(text: str) -> str:
    return _WRAPPER_PATTERN.sub(lambda m: m.group(2), text)


def extract_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    raw = text[3:end].strip()
    parsed = yaml.safe_load(raw) or {}
    return {k: v for k, v in parsed.items() if isinstance(v, str)}


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("---", 3)
    if end == -1:
        return text
    return text[end + 3 :].lstrip("\n")


def transform_body(text: str) -> str:
    """Convert Mintlify JSX components to semantically equivalent Markdown."""
    text = _strip_icons(text)
    for _ in range(_MAX_PASSES):
        prev = text
        text = _transform_callouts(text)
        text = _transform_steps(text)
        text = _transform_tabs(text)
        text = _transform_accordions(text)
        text = _transform_cards(text)
        text = _strip_wrappers(text)
        if text == prev:
            break
    return text
