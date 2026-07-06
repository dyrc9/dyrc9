from __future__ import annotations

import importlib.util
import unittest
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
            "README managed 'Local Quickstarts' section must be regenerated from portfolio.json",
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

## Supporting Repositories

| Repository | Why it matters |
| --- | --- |
| [systems-lab](https://github.com/dyrc9/systems-lab) | Linux kernel lab work and low-level systems exposure. |

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


if __name__ == "__main__":
    unittest.main()
