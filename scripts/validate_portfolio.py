#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "portfolio.json"
SCHEMA_PATH = ROOT / "portfolio.schema.json"
ALLOWED_ACTIVE_CATEGORIES = {"runtime", "workflow-cli", "public-surface"}


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
