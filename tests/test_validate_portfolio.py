from __future__ import annotations

import contextlib
import io
import importlib.util
import json
import unittest
from unittest import mock
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_portfolio.py"
SPEC = importlib.util.spec_from_file_location("validate_portfolio", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ValidatePortfolioReadmeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {
            "owner": "dyrc9",
            "active_products": [
                {
                    "repo": "demo-agent",
                    "url": "https://github.com/dyrc9/demo-agent",
                    "value": "TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.",
                    "status": "working-cli-product",
                    "local_quickstart": [
                        "demo-agent doctor",
                        "demo-agent run sample.txt --out runs/demo-001",
                    ],
                    "proof_commands": [
                        "demo-agent doctor --json",
                        "demo-agent inspect runs/demo-001/result.json --json",
                    ],
                    "artifact_examples": [
                        "result.json with structured output and trace metadata",
                        "summary.md with operator-facing findings",
                    ],
                    "safety_notes": [
                        "manual review before publish",
                        "no policy-evasion automation",
                    ],
                }
            ],
            "shipped_workflow_slices": [
                {
                    "workflow": "Raw idea to publish package",
                    "current_surface": "demo-agent draft, inspect, check",
                    "why_it_matters": "Turns a rough prompt into a reviewable package.",
                }
            ],
            "supporting_repositories": [
                {
                    "repo": "systems-lab",
                    "url": "https://github.com/dyrc9/systems-lab",
                    "why": "Linux kernel lab work and low-level systems exposure.",
                }
            ],
            "next_build_targets": [
                "compact harness lab with pass fail checks",
                "stronger trace review surfaces",
            ],
        }

    def test_validate_readme_accepts_equivalent_table_text(self) -> None:
        readme_text = """
## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [demo-agent](https://github.com/dyrc9/demo-agent) | TypeScript + Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Working CLI product |

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-agent`

TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.

```bash
demo-agent doctor
demo-agent run sample.txt --out runs/demo-001
```

<!-- portfolio-quickstarts:end -->

## Shipped Workflow Slices

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Raw idea to publish package | demo-agent draft, inspect, check | Turns a rough prompt into a reviewable package. |

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-agent`

- `demo-agent doctor --json`
- `demo-agent inspect runs/demo-001/result.json --json`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Linux kernel lab work and low-level systems exposure. |

## Artifact Examples

<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `demo-agent`

- result.json with structured output and trace metadata
- summary.md with operator-facing findings

<!-- portfolio-artifact-examples:end -->

## Safety Guardrails

<!-- portfolio-safety-notes:start -->

These are the explicit guardrails attached to workflow products that could otherwise invite unsafe automation:

### `demo-agent`

- manual review before publish
- no policy-evasion automation

<!-- portfolio-safety-notes:end -->

## Next Build Targets

<!-- portfolio-next-targets:start -->

- compact harness lab with pass fail checks
- stronger trace review surfaces

<!-- portfolio-next-targets:end -->
"""
        errors: list[str] = []

        MODULE.validate_readme(readme_text, self.data, errors)

        self.assertEqual(errors, [])

    def test_validate_readme_rejects_drifted_status(self) -> None:
        readme_text = """
## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [demo-agent](https://github.com/dyrc9/demo-agent) | TypeScript + Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Prototype only |

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-agent`

TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.

```bash
demo-agent doctor
demo-agent run sample.txt --out runs/demo-001
```

<!-- portfolio-quickstarts:end -->

## Shipped Workflow Slices

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Raw idea to publish package | demo-agent draft, inspect, check | Turns a rough prompt into a reviewable package. |

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-agent`

- `demo-agent doctor --json`
- `demo-agent inspect runs/demo-001/result.json --json`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Linux kernel lab work and low-level systems exposure. |

## Artifact Examples

<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `demo-agent`

- result.json with structured output and trace metadata
- summary.md with operator-facing findings

<!-- portfolio-artifact-examples:end -->

## Safety Guardrails

<!-- portfolio-safety-notes:start -->

These are the explicit guardrails attached to workflow products that could otherwise invite unsafe automation:

### `demo-agent`

- manual review before publish
- no policy-evasion automation

<!-- portfolio-safety-notes:end -->

## Next Build Targets

<!-- portfolio-next-targets:start -->

- compact harness lab with pass fail checks
- stronger trace review surfaces

<!-- portfolio-next-targets:end -->
"""
        errors: list[str] = []

        MODULE.validate_readme(readme_text, self.data, errors)

        self.assertIn(
            "README Active Product Surface row 1 status must stay aligned with portfolio.json",
            errors,
        )

    def test_validate_readme_rejects_drifted_workflow_surface(self) -> None:
        readme_text = """
## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [demo-agent](https://github.com/dyrc9/demo-agent) | TypeScript + Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Working CLI product |

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-agent`

TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.

```bash
demo-agent doctor
demo-agent run sample.txt --out runs/demo-001
```

<!-- portfolio-quickstarts:end -->

## Shipped Workflow Slices

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Raw idea to publish package | demo-agent run once | Turns a rough prompt into a reviewable package. |

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-agent`

- `demo-agent doctor --json`
- `demo-agent inspect runs/demo-001/result.json --json`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Linux kernel lab work and low-level systems exposure. |

## Artifact Examples

<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `demo-agent`

- result.json with structured output and trace metadata
- summary.md with operator-facing findings

<!-- portfolio-artifact-examples:end -->

## Safety Guardrails

<!-- portfolio-safety-notes:start -->

These are the explicit guardrails attached to workflow products that could otherwise invite unsafe automation:

### `demo-agent`

- manual review before publish
- no policy-evasion automation

<!-- portfolio-safety-notes:end -->

## Next Build Targets

<!-- portfolio-next-targets:start -->

- compact harness lab with pass fail checks
- stronger trace review surfaces

<!-- portfolio-next-targets:end -->
"""
        errors: list[str] = []

        MODULE.validate_readme(readme_text, self.data, errors)

        self.assertIn(
            "README Shipped Workflow Slices row 1 current surface text must stay aligned with portfolio.json",
            errors,
        )

    def test_render_quickstarts_section_renders_workflow_clis(self) -> None:
        rendered = MODULE.render_quickstarts_section(self.data["active_products"])

        self.assertEqual(
            rendered,
            """<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-agent`

TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.

```bash
demo-agent doctor
demo-agent run sample.txt --out runs/demo-001
```

<!-- portfolio-quickstarts:end -->""",
        )

    def test_render_proof_commands_section_renders_manifest_commands(self) -> None:
        rendered = MODULE.render_proof_commands_section(self.data["active_products"])

        self.assertEqual(
            rendered,
            """<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-agent`

- `demo-agent doctor --json`
- `demo-agent inspect runs/demo-001/result.json --json`

<!-- portfolio-proof-commands:end -->""",
        )

    def test_render_artifact_examples_section_renders_manifest_outputs(self) -> None:
        rendered = MODULE.render_artifact_examples_section(self.data["active_products"])

        self.assertEqual(
            rendered,
            """<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `demo-agent`

- result.json with structured output and trace metadata
- summary.md with operator-facing findings

<!-- portfolio-artifact-examples:end -->""",
        )

    def test_render_safety_notes_section_renders_manifest_guardrails(self) -> None:
        rendered = MODULE.render_safety_notes_section(self.data["active_products"])

        self.assertEqual(
            rendered,
            """<!-- portfolio-safety-notes:start -->

These are the explicit guardrails attached to workflow products that could otherwise invite unsafe automation:

### `demo-agent`

- manual review before publish
- no policy-evasion automation

<!-- portfolio-safety-notes:end -->""",
        )

    def test_render_active_products_table_humanizes_status(self) -> None:
        rendered = MODULE.render_active_products_table(self.data["owner"], self.data["active_products"])

        self.assertEqual(
            rendered,
            """| Repository | Product value | Status |
| --- | --- | --- |
| [demo-agent](https://github.com/dyrc9/demo-agent) | TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Working CLI product |""",
        )

    def test_replace_markdown_table_updates_named_heading(self) -> None:
        readme_text = """## Active Product Surface

intro text

| Repository | Product value | Status |
| --- | --- | --- |
| old | old | old |

## Next Section
"""

        updated = MODULE.replace_markdown_table(
            readme_text,
            "Active Product Surface",
            MODULE.render_active_products_table(self.data["owner"], self.data["active_products"]),
        )

        self.assertIn("| [demo-agent](https://github.com/dyrc9/demo-agent) |", updated)
        self.assertNotIn("| old | old | old |", updated)

    def test_render_next_build_targets_section_renders_bullets(self) -> None:
        rendered = MODULE.render_next_build_targets_section(self.data["next_build_targets"])

        self.assertEqual(
            rendered,
            """<!-- portfolio-next-targets:start -->

- compact harness lab with pass fail checks
- stronger trace review surfaces

<!-- portfolio-next-targets:end -->""",
        )

    def test_validate_readme_rejects_drifted_quickstart_section(self) -> None:
        readme_text = """
## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [demo-agent](https://github.com/dyrc9/demo-agent) | TypeScript + Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Working CLI product |

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-agent`

TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.

```bash
demo-agent run once
```

<!-- portfolio-quickstarts:end -->

## Shipped Workflow Slices

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Raw idea to publish package | demo-agent draft, inspect, check | Turns a rough prompt into a reviewable package. |

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-agent`

- `demo-agent run once`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Linux kernel lab work and low-level systems exposure. |

## Artifact Examples

<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `demo-agent`

- result.json with structured output and trace metadata
- summary.md with operator-facing findings

<!-- portfolio-artifact-examples:end -->

## Safety Guardrails

<!-- portfolio-safety-notes:start -->

These are the explicit guardrails attached to workflow products that could otherwise invite unsafe automation:

### `demo-agent`

- manual review before publish

<!-- portfolio-safety-notes:end -->

## Next Build Targets

<!-- portfolio-next-targets:start -->

- compact harness lab with pass fail checks
- stronger trace review surfaces

<!-- portfolio-next-targets:end -->
"""
        errors: list[str] = []

        MODULE.validate_readme(readme_text, self.data, errors)

        self.assertIn(
            "README managed 'Local Quickstarts' section must be regenerated from portfolio.json",
            errors,
        )

    def test_validate_readme_rejects_drifted_proof_commands_section(self) -> None:
        readme_text = """
## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [demo-agent](https://github.com/dyrc9/demo-agent) | TypeScript + Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Working CLI product |

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-agent`

TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.

```bash
demo-agent doctor
demo-agent run sample.txt --out runs/demo-001
```

<!-- portfolio-quickstarts:end -->

## Shipped Workflow Slices

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Raw idea to publish package | demo-agent draft, inspect, check | Turns a rough prompt into a reviewable package. |

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-agent`

- `demo-agent run once`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Linux kernel lab work and low-level systems exposure. |

## Next Build Targets

<!-- portfolio-next-targets:start -->

- compact harness lab with pass fail checks
- stronger trace review surfaces

<!-- portfolio-next-targets:end -->
"""
        errors: list[str] = []

        MODULE.validate_readme(readme_text, self.data, errors)

        self.assertIn(
            "README managed 'Proof Commands' section must be regenerated from portfolio.json",
            errors,
        )

    def test_validate_readme_rejects_drifted_artifact_examples_section(self) -> None:
        readme_text = """
## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [demo-agent](https://github.com/dyrc9/demo-agent) | TypeScript + Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Working CLI product |

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-agent`

TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.

```bash
demo-agent doctor
demo-agent run sample.txt --out runs/demo-001
```

<!-- portfolio-quickstarts:end -->

## Shipped Workflow Slices

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Raw idea to publish package | demo-agent draft, inspect, check | Turns a rough prompt into a reviewable package. |

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-agent`

- `demo-agent doctor --json`
- `demo-agent inspect runs/demo-001/result.json --json`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Linux kernel lab work and low-level systems exposure. |

## Artifact Examples

<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `demo-agent`

- screenshot.png only

<!-- portfolio-artifact-examples:end -->

## Next Build Targets

<!-- portfolio-next-targets:start -->

- compact harness lab with pass fail checks
- stronger trace review surfaces

<!-- portfolio-next-targets:end -->
"""
        errors: list[str] = []

        MODULE.validate_readme(readme_text, self.data, errors)

        self.assertIn(
            "README managed 'Artifact Examples' section must be regenerated from portfolio.json",
            errors,
        )

    def test_validate_readme_rejects_drifted_safety_notes_section(self) -> None:
        readme_text = """
## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [demo-agent](https://github.com/dyrc9/demo-agent) | TypeScript + Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Working CLI product |

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-agent`

TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.

```bash
demo-agent doctor
demo-agent run sample.txt --out runs/demo-001
```

<!-- portfolio-quickstarts:end -->

## Shipped Workflow Slices

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Raw idea to publish package | demo-agent draft, inspect, check | Turns a rough prompt into a reviewable package. |

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-agent`

- `demo-agent doctor --json`
- `demo-agent inspect runs/demo-001/result.json --json`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Linux kernel lab work and low-level systems exposure. |

## Artifact Examples

<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `demo-agent`

- result.json with structured output and trace metadata
- summary.md with operator-facing findings

<!-- portfolio-artifact-examples:end -->

## Safety Guardrails

<!-- portfolio-safety-notes:start -->

These are the explicit guardrails attached to workflow products that could otherwise invite unsafe automation:

### `demo-agent`

- manual review before publish

<!-- portfolio-safety-notes:end -->

## Next Build Targets

<!-- portfolio-next-targets:start -->

- compact harness lab with pass fail checks
- stronger trace review surfaces

<!-- portfolio-next-targets:end -->
"""
        errors: list[str] = []

        MODULE.validate_readme(readme_text, self.data, errors)

        self.assertIn(
            "README managed 'Safety Guardrails' section must be regenerated from portfolio.json",
            errors,
        )

    def test_validate_readme_rejects_drifted_next_build_targets_section(self) -> None:
        readme_text = """
## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [demo-agent](https://github.com/dyrc9/demo-agent) | TypeScript + Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Working CLI product |

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-agent`

TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems.

```bash
demo-agent doctor
demo-agent run sample.txt --out runs/demo-001
```

<!-- portfolio-quickstarts:end -->

## Shipped Workflow Slices

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Raw idea to publish package | demo-agent draft, inspect, check | Turns a rough prompt into a reviewable package. |

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-agent`

- `demo-agent doctor --json`
- `demo-agent inspect runs/demo-001/result.json --json`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Linux kernel lab work and low-level systems exposure. |

## Artifact Examples

<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `demo-agent`

- result.json with structured output and trace metadata
- summary.md with operator-facing findings

<!-- portfolio-artifact-examples:end -->

## Safety Guardrails

<!-- portfolio-safety-notes:start -->

These are the explicit guardrails attached to workflow products that could otherwise invite unsafe automation:

### `demo-agent`

- manual review before publish
- no policy-evasion automation

<!-- portfolio-safety-notes:end -->

## Next Build Targets

<!-- portfolio-next-targets:start -->

- ship it fast

<!-- portfolio-next-targets:end -->
"""
        errors: list[str] = []

        MODULE.validate_readme(readme_text, self.data, errors)

        self.assertIn(
            "README managed 'Next Build Targets' section must be regenerated from portfolio.json",
            errors,
        )


class ValidatePortfolioSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = MODULE.load_json(MODULE.SCHEMA_PATH)
        self.data = MODULE.load_json(MODULE.PORTFOLIO_PATH)

    def test_schema_accepts_current_manifest(self) -> None:
        errors: list[str] = []

        MODULE.validate_declared_properties(self.data, self.schema, self.schema, errors)

        self.assertEqual(errors, [])

    def test_schema_rejects_unknown_product_fields(self) -> None:
        data = json.loads(json.dumps(self.data))
        data["active_products"][0]["proof_command"] = ["typo should fail closed"]
        errors: list[str] = []

        MODULE.validate_declared_properties(data, self.schema, self.schema, errors)

        self.assertIn(
            "schema $.active_products[0].proof_command: undeclared property is not allowed",
            errors,
        )

    def test_schema_rejects_unknown_nested_fields(self) -> None:
        data = json.loads(json.dumps(self.data))
        data["positioning"]["tagline"] = "undeclared copy"
        errors: list[str] = []

        MODULE.validate_declared_properties(data, self.schema, self.schema, errors)

        self.assertIn(
            "schema $.positioning.tagline: undeclared property is not allowed",
            errors,
        )

    def test_main_json_rejects_unknown_manifest_fields(self) -> None:
        data = json.loads(json.dumps(self.data))
        data["active_products"][0]["unexpected"] = True
        stdout = io.StringIO()

        with (
            mock.patch.object(MODULE, "load_json", side_effect=[data, self.schema]),
            mock.patch.object(MODULE, "load_text", return_value=MODULE.load_text(MODULE.README_PATH)),
            contextlib.redirect_stdout(stdout),
        ):
            exit_code = MODULE.main(["--json"])

        self.assertEqual(exit_code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertIn(
            "schema $.active_products[0].unexpected: undeclared property is not allowed",
            payload["errors"],
        )


class ValidatePortfolioJsonReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {
            "version": 1,
            "owner": "dyrc9",
            "positioning": {
                "headline": "AI Agent / Harness Engineering",
                "summary": "Practical agent tooling.",
            },
            "workflow_pattern": [
                "source input",
                "inspectable artifact",
                "quality gate",
            ],
            "active_products": [
                {
                    "repo": "demo-runtime",
                    "url": "https://github.com/dyrc9/demo-runtime",
                    "category": "runtime",
                    "status": "core-runtime-bet",
                    "value": "Reusable runtime layer for providers, tools, and traces.",
                    "surface": ["providers", "tool orchestration"],
                },
                {
                    "repo": "demo-cli",
                    "url": "https://github.com/dyrc9/demo-cli",
                    "category": "workflow-cli",
                    "status": "working-cli-product",
                    "value": "Workflow CLI with inspectable outputs and quality gates.",
                    "surface": ["run", "inspect", "check"],
                    "local_quickstart": [
                        "demo-cli doctor",
                        "demo-cli run sample.txt --out runs/demo-001",
                    ],
                    "proof_commands": [
                        "demo-cli doctor --json",
                    ],
                    "artifact_examples": [
                        "result.json with trace metadata",
                    ],
                    "safety_notes": [
                        "manual review before publishing",
                    ],
                },
            ],
            "shipped_workflow_slices": [
                {
                    "workflow": "Raw idea -> reviewable package",
                    "current_surface": "demo-cli run, inspect, check",
                    "why_it_matters": "Turns prompts into inspectable artifacts.",
                }
            ],
            "supporting_repositories": [
                {
                    "repo": "systems-lab",
                    "url": "https://github.com/dyrc9/systems-lab",
                    "why": "Systems practice that supports the tooling layer.",
                }
            ],
            "next_build_targets": [
                "trace viewer",
            ],
        }
        self.readme_text = """
## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [demo-runtime](https://github.com/dyrc9/demo-runtime) | Reusable runtime layer for providers, tools, and traces. | Core runtime bet |
| [demo-cli](https://github.com/dyrc9/demo-cli) | Workflow CLI with inspectable outputs and quality gates. | Working CLI product |

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `demo-cli`

Workflow CLI with inspectable outputs and quality gates.

```bash
demo-cli doctor
demo-cli run sample.txt --out runs/demo-001
```

<!-- portfolio-quickstarts:end -->

## Shipped Workflow Slices

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Raw idea -> reviewable package | demo-cli run, inspect, check | Turns prompts into inspectable artifacts. |

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `demo-cli`

- `demo-cli doctor --json`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Systems practice that supports the tooling layer. |

## Artifact Examples

<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `demo-cli`

- result.json with trace metadata

<!-- portfolio-artifact-examples:end -->

## Safety Guardrails

<!-- portfolio-safety-notes:start -->

These are the explicit guardrails attached to workflow products that could otherwise invite unsafe automation:

### `demo-cli`

- manual review before publishing

<!-- portfolio-safety-notes:end -->

## Next Build Targets

<!-- portfolio-next-targets:start -->

- trace viewer

<!-- portfolio-next-targets:end -->
"""

    def test_build_report_summarizes_portfolio_health(self) -> None:
        errors: list[str] = []

        MODULE.validate_top_level(self.data, errors)
        MODULE.validate_active_products("dyrc9", self.data["active_products"], errors)
        MODULE.validate_supporting_repositories("dyrc9", self.data["supporting_repositories"], errors)
        MODULE.validate_readme(self.readme_text, self.data, errors)
        report = MODULE.build_report(self.data, errors)

        self.assertEqual(
            report,
            {
                "ok": True,
                "owner": "dyrc9",
                "counts": {
                    "active_products": 2,
                    "workflow_slices": 1,
                    "supporting_repositories": 1,
                    "next_build_targets": 1,
                },
                "active_product_categories": {
                    "runtime": 1,
                    "workflow-cli": 1,
                },
                "workflow_cli_repos": ["demo-cli"],
                "workflow_cli_with_operator_docs": ["demo-cli"],
                "workflow_cli_missing_operator_docs": {},
                "repos_with_proof_commands": ["demo-cli"],
                "repos_with_artifact_examples": ["demo-cli"],
                "repos_with_safety_notes": ["demo-cli"],
                "readme_in_sync": True,
                "errors": [],
            },
        )

    def test_main_json_outputs_machine_readable_failures(self) -> None:
        broken_readme = self.readme_text.replace("manual review before publishing", "skip review")
        stdout = io.StringIO()
        stderr = io.StringIO()

        with (
            mock.patch.object(MODULE, "load_json", side_effect=[self.data, {}]),
            mock.patch.object(MODULE, "load_text", return_value=broken_readme),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            exit_code = MODULE.main(["--json"])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr.getvalue(), "")

        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])
        self.assertFalse(payload["readme_in_sync"])
        self.assertEqual(payload["workflow_cli_repos"], ["demo-cli"])
        self.assertEqual(payload["workflow_cli_with_operator_docs"], ["demo-cli"])
        self.assertEqual(payload["workflow_cli_missing_operator_docs"], {})
        self.assertIn(
            "README managed 'Safety Guardrails' section must be regenerated from portfolio.json",
            payload["errors"],
        )

    def test_validate_active_products_requires_workflow_cli_proof_commands(self) -> None:
        data = json.loads(json.dumps(self.data))
        del data["active_products"][1]["proof_commands"]

        errors: list[str] = []

        MODULE.validate_active_products(data["owner"], data["active_products"], errors)

        self.assertIn(
            "active_products[1].proof_commands is required for workflow-cli products",
            errors,
        )

    def test_validate_active_products_requires_workflow_cli_artifact_examples(self) -> None:
        data = json.loads(json.dumps(self.data))
        del data["active_products"][1]["artifact_examples"]

        errors: list[str] = []

        MODULE.validate_active_products(data["owner"], data["active_products"], errors)

        self.assertIn(
            "active_products[1].artifact_examples is required for workflow-cli products",
            errors,
        )

    def test_validate_active_products_rejects_duplicate_operator_docs(self) -> None:
        product = {
            "repo": "demo-cli",
            "url": "https://github.com/dyrc9/demo-cli",
            "category": "workflow-cli",
            "status": "working-cli-product",
            "value": "A demo workflow.",
            "surface": ["run", "run"],
            "local_quickstart": ["demo-cli doctor", "demo-cli doctor"],
            "proof_commands": ["demo-cli check sample.json", "demo-cli check sample.json"],
            "artifact_examples": ["result.json", "result.json"],
        }
        errors: list[str] = []

        MODULE.validate_active_products("dyrc9", [product], errors)

        for field in ("surface", "local_quickstart", "proof_commands", "artifact_examples"):
            self.assertIn(f"active_products[0].{field} entries must be unique", errors)

    def test_validate_active_products_requires_commands_to_invoke_product_cli(self) -> None:
        product = {
            "repo": "demo-cli",
            "url": "https://github.com/dyrc9/demo-cli",
            "category": "workflow-cli",
            "status": "working-cli-product",
            "value": "A demo workflow.",
            "surface": ["run"],
            "local_quickstart": ["python scripts/demo.py"],
            "proof_commands": ["other-cli check sample.json"],
            "artifact_examples": ["result.json"],
        }
        errors: list[str] = []

        MODULE.validate_active_products("dyrc9", [product], errors)

        self.assertIn("active_products[0].local_quickstart[0] must invoke the demo-cli CLI", errors)
        self.assertIn("active_products[0].proof_commands[0] must invoke the demo-cli CLI", errors)

    def test_build_report_tracks_workflow_cli_operator_doc_gaps(self) -> None:
        data = json.loads(json.dumps(self.data))
        del data["active_products"][1]["artifact_examples"]
        errors = ["active_products[1].artifact_examples is required for workflow-cli products"]

        report = MODULE.build_report(data, errors)

        self.assertEqual(report["workflow_cli_repos"], ["demo-cli"])
        self.assertEqual(report["workflow_cli_with_operator_docs"], [])
        self.assertEqual(
            report["workflow_cli_missing_operator_docs"],
            {"demo-cli": ["artifact_examples"]},
        )


if __name__ == "__main__":
    unittest.main()
