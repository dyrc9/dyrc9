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


def validate_readme(readme_text: str, data: dict[str, object], errors: list[str]) -> None:
    active_products = data.get("active_products")
    if isinstance(data.get("owner"), str) and isinstance(active_products, list):
        validate_readme_active_products_table(data["owner"], active_products, readme_text, errors)

    supporting_repositories = data.get("supporting_repositories")
    if isinstance(data.get("owner"), str) and isinstance(supporting_repositories, list):
        validate_readme_supporting_repositories_table(data["owner"], supporting_repositories, readme_text, errors)


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


def main() -> int:
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
        f"{len(data['supporting_repositories'])} supporting repositories, "
        f"{len(data['next_build_targets'])} next targets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
