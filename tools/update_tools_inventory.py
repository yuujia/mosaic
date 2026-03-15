#!/usr/bin/env python3
"""Generate a Markdown inventory of Mosaic Python tools.

This scans `tools/*.py` and writes `00_config/TOOLS_INVENTORY.md` with a
short purpose and a standard command for each tool.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ToolInfo:
    """Metadata for one Python tool script."""

    path: Path
    purpose: str
    run_cmd: str


def first_sentence(text: str) -> str:
    """Return a compact first sentence from freeform text."""
    cleaned = " ".join((text or "").strip().split())
    if not cleaned:
        return ""
    for sep in [". ", "\n"]:
        idx = cleaned.find(sep)
        if idx > 0:
            return cleaned[: idx + 1]
    return cleaned


def module_docstring(path: Path) -> str:
    """Read a module docstring from a Python file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return ""
    return ast.get_docstring(tree) or ""


def argparse_description(path: Path) -> str:
    """Extract argparse ArgumentParser(description=...) if statically defined."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return ""

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        is_parser_ctor = False
        if isinstance(func, ast.Attribute):
            is_parser_ctor = func.attr == "ArgumentParser"
        elif isinstance(func, ast.Name):
            is_parser_ctor = func.id == "ArgumentParser"

        if not is_parser_ctor:
            continue

        for kw in node.keywords:
            if kw.arg != "description":
                continue
            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                return kw.value.value.strip()
    return ""


def detect_purpose(path: Path) -> str:
    """Choose the best available summary for a script's purpose."""
    doc = first_sentence(module_docstring(path))
    if doc:
        return doc
    desc = first_sentence(argparse_description(path))
    if desc:
        return desc
    return "No summary found. Add a module docstring or argparse description."


def render_inventory(root: Path, tools: list[ToolInfo]) -> str:
    """Render the Markdown inventory document."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines: list[str] = [
        "# Mosaic Tools Inventory",
        "",
        f"Generated (UTC): {ts}",
        f"Mosaic root: `{root}`",
        "",
        "## Python Tools",
        "",
    ]

    if not tools:
        lines.append("_No Python tools found in `tools/`._")
        lines.append("")
        return "\n".join(lines)

    for tool in tools:
        rel = tool.path.relative_to(root)
        lines.append(f"### `{rel}`")
        lines.append(f"- Purpose: {tool.purpose}")
        lines.append(f"- How to run: `{tool.run_cmd}`")
        lines.append("")

    return "\n".join(lines)


def collect_tools(root: Path) -> list[ToolInfo]:
    """Collect Python tools from `tools/`."""
    tools_dir = root / "tools"
    if not tools_dir.exists():
        return []

    out: list[ToolInfo] = []
    for path in sorted(tools_dir.glob("*.py")):
        rel = path.relative_to(root)
        out.append(
            ToolInfo(
                path=path,
                purpose=detect_purpose(path),
                run_cmd=f"python {rel} --help",
            )
        )
    return out


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Mosaic's Python tools inventory markdown file."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to Mosaic root folder (default: script parent).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("00_config") / "TOOLS_INVENTORY.md",
        help="Output path relative to --root unless absolute.",
    )
    return parser.parse_args()


def main() -> int:
    """Generate the tools inventory file."""
    args = parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else (root / args.output)

    tools = collect_tools(root)
    inventory = render_inventory(root, tools)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(inventory, encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Tools indexed: {len(tools)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
