#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "portfolio.json"
SCHEMA_PATH = ROOT / "portfolio.schema.json"
README_PATH = ROOT / "README.md"
ALLOWED_ACTIVE_CATEGORIES = {"runtime", "workflow-cli", "public-surface"}
QUICKSTART_START_MARKER = "<!-- portfolio-quickstarts:start -->"
QUICKSTART_END_MARKER = "<!-- portfolio-quickstarts:end -->"
NEXT_TARGETS_START_MARKER = "<!-- portfolio-next-targets:start -->"
NEXT_TARGETS_END_MARKER = "<!-- portfolio-next-targets:end -->"


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        return handle.read()


def ensure(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(is_non_empty_string(item) for item in value)


def validate_top_level(data: dict[str, object], errors: list[str]) -> None:
    required = {
        "version",
        "owner",
        "positioning",
        "workflow_pattern",
        "active_products",
        "shipped_workflow_slices",
        "supporting_repositories",
        "next_build_targets",
    }
    missing = sorted(required.difference(data))
    ensure(not missing, f"missing top-level keys: {', '.join(missing)}", errors)

    ensure(isinstance(data.get("version"), int) and data["version"] >= 1, "version must be an integer >= 1", errors)
    ensure(is_non_empty_string(data.get("owner")), "owner must be a non-empty string", errors)

    positioning = data.get("positioning")
    ensure(isinstance(positioning, dict), "positioning must be an object", errors)
    if isinstance(positioning, dict):
        ensure(is_non_empty_string(positioning.get("headline")), "positioning.headline must be a non-empty string", errors)
        ensure(is_non_empty_string(positioning.get("summary")), "positioning.summary must be a non-empty string", errors)

    workflow_pattern = data.get("workflow_pattern")
    ensure(is_string_list(workflow_pattern), "workflow_pattern must be a non-empty list of strings", errors)
    if isinstance(workflow_pattern, list):
        normalized = [item.strip() for item in workflow_pattern if isinstance(item, str)]
        ensure(len(normalized) == len(set(normalized)), "workflow_pattern entries must be unique", errors)

    validate_workflow_slices(data.get("shipped_workflow_slices"), errors)
    ensure(is_string_list(data.get("next_build_targets")), "next_build_targets must be a non-empty list of strings", errors)


def expected_github_url(owner: str, repo: str) -> str:
    return f"https://github.com/{owner}/{repo}"


def normalize_comparable_text(value: str) -> str:
    collapsed = value.lower()
    collapsed = collapsed.replace("+", " and ")
    collapsed = collapsed.replace("/", " and ")
    collapsed = collapsed.replace("&", " and ")
    collapsed = re.sub(r"[^a-z0-9]+", " ", collapsed)
    return " ".join(collapsed.split())


def extract_markdown_table(readme_text: str, heading: str) -> tuple[list[str], list[list[str]]] | None:
    lines = readme_text.splitlines()
    heading_line = f"## {heading}"

    for index, line in enumerate(lines):
        if line.strip() != heading_line:
            continue

        cursor = index + 1
        while cursor < len(lines):
            stripped = lines[cursor].strip()
            if stripped.startswith("## "):
                return None
            if lines[cursor].lstrip().startswith("|"):
                table_lines: list[str] = []
                while cursor < len(lines) and lines[cursor].lstrip().startswith("|"):
                    table_lines.append(lines[cursor].strip())
                    cursor += 1

                if len(table_lines) < 2:
                    return None

                parsed_rows = [parse_markdown_row(table_line) for table_line in table_lines]
                return parsed_rows[0], parsed_rows[2:]

            cursor += 1

    return None


def parse_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_markdown_link(cell: str) -> tuple[str, str] | None:
    match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", cell.strip())
    if not match:
        return None
    return match.group(1), match.group(2)


def render_quickstarts_section(products: list[object]) -> str:
    lines = [
        QUICKSTART_START_MARKER,
        "",
        "Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:",
        "",
    ]

    rendered_any = False
    for product in products:
        if not isinstance(product, dict):
            continue

        quickstart = product.get("local_quickstart")
        if not is_string_list(quickstart):
            continue

        repo = product.get("repo")
        value = product.get("value")
        if not isinstance(repo, str) or not isinstance(value, str):
            continue

        rendered_any = True
        lines.append(f"### `{repo}`")
        lines.append("")
        lines.append(value)
        lines.append("")
        lines.append("```bash")
        lines.extend(quickstart)
        lines.append("```")
        lines.append("")

    if not rendered_any:
        lines.append("_No workflow CLI quickstarts are currently defined in the manifest._")
        lines.append("")

    lines.append(QUICKSTART_END_MARKER)
    return "\n".join(lines)


def render_next_build_targets_section(targets: list[object]) -> str:
    lines = [
        NEXT_TARGETS_START_MARKER,
        "",
    ]

    if is_string_list(targets):
        for target in targets:
            lines.append(f"- {target}")
    else:
        lines.append("_No next build targets are currently defined in the manifest._")

    lines.append("")
    lines.append(NEXT_TARGETS_END_MARKER)
    return "\n".join(lines)


def replace_managed_section(readme_text: str, start_marker: str, end_marker: str, rendered_section: str) -> str:
    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
        re.DOTALL,
    )
    if not pattern.search(readme_text):
        raise ValueError(f"README is missing managed section markers: {start_marker} .. {end_marker}")
    return pattern.sub(rendered_section, readme_text, count=1)


def validate_readme_quickstarts_section(products: list[object], readme_text: str, errors: list[str]) -> None:
    rendered_section = render_quickstarts_section(products)
    pattern = re.compile(
        rf"{re.escape(QUICKSTART_START_MARKER)}.*?{re.escape(QUICKSTART_END_MARKER)}",
        re.DOTALL,
    )
    match = pattern.search(readme_text)
    ensure(match is not None, "README is missing the managed 'Local Quickstarts' section markers", errors)
    if match is None:
        return

    current_section = match.group(0)
    ensure(
        current_section == rendered_section,
        "README managed 'Local Quickstarts' section must be regenerated from portfolio.json",
        errors,
    )


def validate_readme_next_build_targets_section(targets: list[object], readme_text: str, errors: list[str]) -> None:
    rendered_section = render_next_build_targets_section(targets)
    pattern = re.compile(
        rf"{re.escape(NEXT_TARGETS_START_MARKER)}.*?{re.escape(NEXT_TARGETS_END_MARKER)}",
        re.DOTALL,
    )
    match = pattern.search(readme_text)
    ensure(match is not None, "README is missing the managed 'Next Build Targets' section markers", errors)
    if match is None:
        return

    current_section = match.group(0)
    ensure(
        current_section == rendered_section,
        "README managed 'Next Build Targets' section must be regenerated from portfolio.json",
        errors,
    )


def validate_active_products(owner: str, products: object, errors: list[str]) -> None:
    ensure(isinstance(products, list) and bool(products), "active_products must be a non-empty list", errors)
    if not isinstance(products, list):
        return

    seen_repos: set[str] = set()
    for index, product in enumerate(products):
        prefix = f"active_products[{index}]"
        ensure(isinstance(product, dict), f"{prefix} must be an object", errors)
        if not isinstance(product, dict):
            continue

        repo = product.get("repo")
        ensure(is_non_empty_string(repo), f"{prefix}.repo must be a non-empty string", errors)
        if isinstance(repo, str):
            ensure(repo not in seen_repos, f"{prefix}.repo must be unique: {repo}", errors)
            seen_repos.add(repo)

        category = product.get("category")
        ensure(category in ALLOWED_ACTIVE_CATEGORIES, f"{prefix}.category must be one of {sorted(ALLOWED_ACTIVE_CATEGORIES)}", errors)
        ensure(is_non_empty_string(product.get("status")), f"{prefix}.status must be a non-empty string", errors)
        ensure(is_non_empty_string(product.get("value")), f"{prefix}.value must be a non-empty string", errors)
        ensure(is_string_list(product.get("surface")), f"{prefix}.surface must be a non-empty list of strings", errors)

        url = product.get("url")
        ensure(is_non_empty_string(url), f"{prefix}.url must be a non-empty string", errors)
        if isinstance(repo, str) and isinstance(url, str):
            ensure(url == expected_github_url(owner, repo), f"{prefix}.url must match owner/repo: {expected_github_url(owner, repo)}", errors)

        if category == "workflow-cli":
            ensure(is_string_list(product.get("local_quickstart")), f"{prefix}.local_quickstart is required for workflow-cli products", errors)

        if "local_quickstart" in product and product.get("local_quickstart") is not None:
            ensure(is_string_list(product.get("local_quickstart")), f"{prefix}.local_quickstart must be a non-empty list of strings", errors)

        if "safety_notes" in product and product.get("safety_notes") is not None:
            ensure(is_string_list(product.get("safety_notes")), f"{prefix}.safety_notes must be a non-empty list of strings", errors)


def validate_supporting_repositories(owner: str, repositories: object, errors: list[str]) -> None:
    ensure(isinstance(repositories, list), "supporting_repositories must be a list", errors)
    if not isinstance(repositories, list):
        return

    seen_repos: set[str] = set()
    for index, repo_entry in enumerate(repositories):
        prefix = f"supporting_repositories[{index}]"
        ensure(isinstance(repo_entry, dict), f"{prefix} must be an object", errors)
        if not isinstance(repo_entry, dict):
            continue

        repo = repo_entry.get("repo")
        url = repo_entry.get("url")
        ensure(is_non_empty_string(repo), f"{prefix}.repo must be a non-empty string", errors)
        ensure(is_non_empty_string(url), f"{prefix}.url must be a non-empty string", errors)
        ensure(is_non_empty_string(repo_entry.get("why")), f"{prefix}.why must be a non-empty string", errors)

        if isinstance(repo, str):
            ensure(repo not in seen_repos, f"{prefix}.repo must be unique: {repo}", errors)
            seen_repos.add(repo)

        if isinstance(repo, str) and isinstance(url, str):
            ensure(url == expected_github_url(owner, repo), f"{prefix}.url must match owner/repo: {expected_github_url(owner, repo)}", errors)


def validate_workflow_slices(workflow_slices: object, errors: list[str]) -> None:
    ensure(isinstance(workflow_slices, list) and bool(workflow_slices), "shipped_workflow_slices must be a non-empty list", errors)
    if not isinstance(workflow_slices, list):
        return

    seen_workflows: set[str] = set()
    for index, workflow_slice in enumerate(workflow_slices):
        prefix = f"shipped_workflow_slices[{index}]"
        ensure(isinstance(workflow_slice, dict), f"{prefix} must be an object", errors)
        if not isinstance(workflow_slice, dict):
            continue

        workflow = workflow_slice.get("workflow")
        ensure(is_non_empty_string(workflow), f"{prefix}.workflow must be a non-empty string", errors)
        ensure(is_non_empty_string(workflow_slice.get("current_surface")), f"{prefix}.current_surface must be a non-empty string", errors)
        ensure(is_non_empty_string(workflow_slice.get("why_it_matters")), f"{prefix}.why_it_matters must be a non-empty string", errors)

        if isinstance(workflow, str):
            ensure(workflow not in seen_workflows, f"{prefix}.workflow must be unique: {workflow}", errors)
            seen_workflows.add(workflow)


def validate_readme(readme_text: str, data: dict[str, object], errors: list[str]) -> None:
    active_products = data.get("active_products")
    if isinstance(data.get("owner"), str) and isinstance(active_products, list):
        validate_readme_active_products_table(data["owner"], active_products, readme_text, errors)
        validate_readme_quickstarts_section(active_products, readme_text, errors)

    workflow_slices = data.get("shipped_workflow_slices")
    if isinstance(workflow_slices, list):
        validate_readme_workflow_slices_table(workflow_slices, readme_text, errors)

    supporting_repositories = data.get("supporting_repositories")
    if isinstance(data.get("owner"), str) and isinstance(supporting_repositories, list):
        validate_readme_supporting_repositories_table(data["owner"], supporting_repositories, readme_text, errors)

    next_build_targets = data.get("next_build_targets")
    if isinstance(next_build_targets, list):
        validate_readme_next_build_targets_section(next_build_targets, readme_text, errors)


def validate_readme_active_products_table(owner: str, products: list[object], readme_text: str, errors: list[str]) -> None:
    parsed = extract_markdown_table(readme_text, "Active Product Surface")
    ensure(parsed is not None, "README is missing the 'Active Product Surface' table", errors)
    if parsed is None:
        return

    headers, rows = parsed
    ensure(headers == ["Repository", "Product value", "Status"], "README 'Active Product Surface' headers must be: Repository | Product value | Status", errors)
    ensure(len(rows) == len(products), "README 'Active Product Surface' row count must match active_products", errors)
    if len(rows) != len(products):
        return

    for index, (product, row) in enumerate(zip(products, rows)):
        prefix = f"README Active Product Surface row {index + 1}"
        if not isinstance(product, dict):
            errors.append(f"{prefix} cannot be validated because active_products[{index}] is not an object")
            continue

        ensure(len(row) == 3, f"{prefix} must have exactly 3 columns", errors)
        if len(row) != 3:
            continue

        repo_cell, value_cell, status_cell = row
        link = parse_markdown_link(repo_cell)
        ensure(link is not None, f"{prefix} repository cell must be a Markdown link", errors)
        if link is None:
            continue

        repo_label, repo_url = link
        expected_repo = product.get("repo")
        expected_url = product.get("url")
        expected_value = product.get("value")
        expected_status = product.get("status")

        if isinstance(expected_repo, str):
            ensure(repo_label == expected_repo, f"{prefix} repository label must be '{expected_repo}'", errors)
        if isinstance(expected_url, str):
            ensure(repo_url == expected_url == expected_github_url(owner, repo_label), f"{prefix} repository URL must match manifest owner/repo", errors)
        if isinstance(expected_value, str):
            ensure(
                normalize_comparable_text(value_cell) == normalize_comparable_text(expected_value),
                f"{prefix} product value must stay aligned with portfolio.json",
                errors,
            )
        if isinstance(expected_status, str):
            ensure(
                normalize_comparable_text(status_cell) == normalize_comparable_text(expected_status),
                f"{prefix} status must stay aligned with portfolio.json",
                errors,
            )


def validate_readme_supporting_repositories_table(owner: str, repositories: list[object], readme_text: str, errors: list[str]) -> None:
    parsed = extract_markdown_table(readme_text, "Supporting Repositories")
    ensure(parsed is not None, "README is missing the 'Supporting Repositories' table", errors)
    if parsed is None:
        return

    headers, rows = parsed
    ensure(headers == ["Repository", "Why it matters"], "README 'Supporting Repositories' headers must be: Repository | Why it matters", errors)
    ensure(len(rows) == len(repositories), "README 'Supporting Repositories' row count must match supporting_repositories", errors)
    if len(rows) != len(repositories):
        return

    for index, (repository, row) in enumerate(zip(repositories, rows)):
        prefix = f"README Supporting Repositories row {index + 1}"
        if not isinstance(repository, dict):
            errors.append(f"{prefix} cannot be validated because supporting_repositories[{index}] is not an object")
            continue

        ensure(len(row) == 2, f"{prefix} must have exactly 2 columns", errors)
        if len(row) != 2:
            continue

        repo_cell, why_cell = row
        link = parse_markdown_link(repo_cell)
        ensure(link is not None, f"{prefix} repository cell must be a Markdown link", errors)
        if link is None:
            continue

        repo_label, repo_url = link
        expected_repo = repository.get("repo")
        expected_url = repository.get("url")
        expected_why = repository.get("why")

        if isinstance(expected_repo, str):
            ensure(repo_label == expected_repo, f"{prefix} repository label must be '{expected_repo}'", errors)
        if isinstance(expected_url, str):
            ensure(repo_url == expected_url == expected_github_url(owner, repo_label), f"{prefix} repository URL must match manifest owner/repo", errors)
        if isinstance(expected_why, str):
            ensure(
                normalize_comparable_text(why_cell) == normalize_comparable_text(expected_why),
                f"{prefix} why text must stay aligned with portfolio.json",
                errors,
            )


def validate_readme_workflow_slices_table(workflow_slices: list[object], readme_text: str, errors: list[str]) -> None:
    parsed = extract_markdown_table(readme_text, "Shipped Workflow Slices")
    ensure(parsed is not None, "README is missing the 'Shipped Workflow Slices' table", errors)
    if parsed is None:
        return

    headers, rows = parsed
    ensure(headers == ["Workflow", "Current surface", "Why it matters"], "README 'Shipped Workflow Slices' headers must be: Workflow | Current surface | Why it matters", errors)
    ensure(len(rows) == len(workflow_slices), "README 'Shipped Workflow Slices' row count must match shipped_workflow_slices", errors)
    if len(rows) != len(workflow_slices):
        return

    for index, (workflow_slice, row) in enumerate(zip(workflow_slices, rows)):
        prefix = f"README Shipped Workflow Slices row {index + 1}"
        if not isinstance(workflow_slice, dict):
            errors.append(f"{prefix} cannot be validated because shipped_workflow_slices[{index}] is not an object")
            continue

        ensure(len(row) == 3, f"{prefix} must have exactly 3 columns", errors)
        if len(row) != 3:
            continue

        workflow_cell, current_surface_cell, why_cell = row
        expected_workflow = workflow_slice.get("workflow")
        expected_surface = workflow_slice.get("current_surface")
        expected_why = workflow_slice.get("why_it_matters")

        if isinstance(expected_workflow, str):
            ensure(
                normalize_comparable_text(workflow_cell) == normalize_comparable_text(expected_workflow),
                f"{prefix} workflow text must stay aligned with portfolio.json",
                errors,
            )
        if isinstance(expected_surface, str):
            ensure(
                normalize_comparable_text(current_surface_cell) == normalize_comparable_text(expected_surface),
                f"{prefix} current surface text must stay aligned with portfolio.json",
                errors,
            )
        if isinstance(expected_why, str):
            ensure(
                normalize_comparable_text(why_cell) == normalize_comparable_text(expected_why),
                f"{prefix} why text must stay aligned with portfolio.json",
                errors,
            )


def sync_readme(data: dict[str, object]) -> int:
    active_products = data.get("active_products")
    if not isinstance(active_products, list):
        print("portfolio.json is missing a valid active_products list", file=sys.stderr)
        return 1

    next_build_targets = data.get("next_build_targets")
    if not isinstance(next_build_targets, list):
        print("portfolio.json is missing a valid next_build_targets list", file=sys.stderr)
        return 1

    try:
        readme_text = load_text(README_PATH)
    except FileNotFoundError:
        print(f"missing file: {README_PATH}", file=sys.stderr)
        return 1

    try:
        updated_readme = replace_managed_section(
            readme_text,
            QUICKSTART_START_MARKER,
            QUICKSTART_END_MARKER,
            render_quickstarts_section(active_products),
        )
        updated_readme = replace_managed_section(
            updated_readme,
            NEXT_TARGETS_START_MARKER,
            NEXT_TARGETS_END_MARKER,
            render_next_build_targets_section(next_build_targets),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if updated_readme != readme_text:
        README_PATH.write_text(updated_readme, encoding="utf-8")
        print("synced README managed sections from portfolio.json")
    else:
        print("README managed sections already up to date")

    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    errors: list[str] = []

    try:
        data = load_json(PORTFOLIO_PATH)
    except FileNotFoundError:
        print(f"missing file: {PORTFOLIO_PATH}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"invalid JSON in {PORTFOLIO_PATH}: {exc}", file=sys.stderr)
        return 1

    try:
        load_json(SCHEMA_PATH)
    except FileNotFoundError:
        print(f"missing file: {SCHEMA_PATH}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"invalid JSON in {SCHEMA_PATH}: {exc}", file=sys.stderr)
        return 1

    try:
        readme_text = load_text(README_PATH)
    except FileNotFoundError:
        print(f"missing file: {README_PATH}", file=sys.stderr)
        return 1

    ensure(isinstance(data, dict), "portfolio.json must contain a top-level object", errors)
    if not isinstance(data, dict):
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if argv == ["--sync-readme"]:
        return sync_readme(data)

    validate_top_level(data, errors)

    owner = data.get("owner")
    if isinstance(owner, str):
        validate_active_products(owner, data.get("active_products"), errors)
        validate_supporting_repositories(owner, data.get("supporting_repositories"), errors)
        validate_readme(readme_text, data, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "portfolio manifest OK: "
        f"{len(data['active_products'])} active products, "
        f"{len(data['shipped_workflow_slices'])} workflow slices, "
        f"{len(data['supporting_repositories'])} supporting repositories, "
        f"{len(data['next_build_targets'])} next targets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
