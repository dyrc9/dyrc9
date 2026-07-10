# dyrc9 - AI Agent / Harness Engineering

I build practical agent tooling: the layer where models are wired into real workflows, checked for regressions, and forced to produce durable outputs instead of demos.

This profile is a product portfolio, not a trend scrapbook. The repos below are the ones that support that story.

- agent harnesses and workflow runners
- evaluation loops, traces, and regression checks
- CLI-first automations with durable artifacts
- systems and security fundamentals underneath the agent layer

## Current Focus

| Area | Current direction |
| --- | --- |
| Agent Harness | provider contracts, tool orchestration, replayable workflows |
| Evaluation | behavior checks, summary quality, regression suites, trace review |
| Automation | local CLI tools, batch jobs, inspectable outputs |
| Systems | networking, Linux internals, observability, security experiments |

## Active Product Surface

| Repository | Product value | Status |
| --- | --- | --- |
| [sushi-agent](https://github.com/dyrc9/sushi-agent) | TypeScript and Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Core runtime bet |
| [agent-meeting-notes](https://github.com/dyrc9/agent-meeting-notes) | Long-audio transcription and meeting-notes harness with chunking, structured outputs, and exportable artifacts. | Working CLI product |
| [xhs-content-agent](https://github.com/dyrc9/xhs-content-agent) | Human-reviewed content pipeline for Xiaohongshu and RedNote drafts, calendars, and publish packages. | Working CLI product |
| [dyrc9.github.io](https://github.com/dyrc9/dyrc9.github.io) | Personal site and long-term public surface for demos, notes, and portfolio framing. | Public narrative layer |

## Shipped Workflow Slices

These are the smallest product surfaces that already exist and show how I think about operator-facing agent tooling:

| Workflow | Current surface | Why it matters |
| --- | --- | --- |
| Long meeting -> inspectable notes | agent-meeting-notes run, probe, estimate, inspect, check | Turns a multi-hour recording into reusable transcript and summary artifacts with preflight and quality gates. |
| Raw idea -> publish package | xhs-content-agent draft, calendar, titles, inspect, check | Treats creator work as a reviewable pipeline instead of one-shot prompting or unsafe automation. |
| Provider/tool runtime embedding | sushi-agent runtime and local tools | Pushes toward a reusable execution layer where models, tools, and traces can be composed inside real systems. |

The common pattern is consistent:

```text
source input -> staged processing -> inspectable artifact -> quality gate -> human or system decision
```

## Portfolio Manifest

The profile now also has a machine-readable index in [`portfolio.json`](./portfolio.json).

It exists so this repository can drive more than a static README:

- the public site can reuse one source of truth for featured repos
- automation can diff actual product status instead of scraping prose
- future harness or eval work can select example products by category and surface area

That keeps the narrative and the product inventory aligned as the portfolio changes.

## Local Quickstarts

<!-- portfolio-quickstarts:start -->

Use these local commands to demonstrate the operator-facing surfaces of the workflow CLIs:

### `agent-meeting-notes`

Long-audio transcription and meeting-notes harness with chunking, structured outputs, and exportable artifacts.

```bash
agent-meeting-notes doctor
agent-meeting-notes run path/to/meeting.mp3 --out runs/meeting-001 --transcriber openai --summarizer openai
```

### `xhs-content-agent`

Human-reviewed content pipeline for Xiaohongshu and RedNote drafts, calendars, and publish packages.

```bash
xhs-content-agent doctor
xhs-content-agent draft examples/idea.md --out runs/first-note
```

<!-- portfolio-quickstarts:end -->

The manifest and the README product tables are now checked by a local validator and CI:

```bash
python scripts/validate_portfolio.py
python scripts/validate_portfolio.py --sync-readme
python -m unittest tests.test_validate_portfolio
```

The structure contract lives in [`portfolio.schema.json`](./portfolio.schema.json), while the validator enforces a few repository-specific rules such as owner/repo URL consistency and `local_quickstart` coverage for workflow CLIs.

## Proof Commands

<!-- portfolio-proof-commands:start -->

Run these commands to show concrete operator-facing behavior, preflight checks, and quality gates:

### `agent-meeting-notes`

- `agent-meeting-notes doctor --json`
- `agent-meeting-notes probe meeting.mp3 --json`
- `agent-meeting-notes estimate meeting.mp3 --chunk-seconds 600`
- `agent-meeting-notes check examples/transcript.md`

### `xhs-content-agent`

- `xhs-content-agent doctor --json`
- `xhs-content-agent draft examples/idea.md --generator template --out runs/template-note`
- `xhs-content-agent inspect runs/template-note/note.json --json`
- `xhs-content-agent check runs/template-note/note.json --json --strict`

<!-- portfolio-proof-commands:end -->

## Supporting Repositories

These are relevant because they reinforce the engineering foundation behind the product work:

| Repository | Why it matters |
| --- | --- |
| [console-chat-gpt](https://github.com/dyrc9/console-chat-gpt) | Early CLI experiments around chat APIs and terminal interaction patterns. |
| [cwym](https://github.com/dyrc9/cwym) | Networking and message-oriented systems practice. |
| [CS353Project2](https://github.com/dyrc9/CS353Project2) | Linux kernel lab work and low-level systems exposure. |
| [Kitsune_prp](https://github.com/dyrc9/Kitsune_prp) | Security and intrusion-detection related exploration. |

Older forks and course repositories are being cleaned up so the profile stays product-focused.

## Artifact Examples

<!-- portfolio-artifact-examples:start -->

These are the concrete files or outputs an operator should expect from the workflow products:

### `agent-meeting-notes`

- transcript.md with timestamps and speaker-attributed segments
- summary.md with decisions, action items, and risks
- notes.json with structured metadata for downstream review

### `xhs-content-agent`

- note.json draft package with title, body, hashtags, and metadata
- calendar.csv or markdown planning output for reviewable scheduling
- diagnostic JSON from inspect and check commands for operator signoff

<!-- portfolio-artifact-examples:end -->

## Stack I Am Using More

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?style=flat&logo=rust&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=000)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=000)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)

## What This Portfolio Optimizes For

- small tools that solve a real workflow problem
- reproducible runs instead of screenshot-only demos
- outputs that can be inspected, exported, and reviewed later
- engineering notes that explain tradeoffs, failures, and fixes
- products that make agent behavior easier to trust and operate
- product slices that can be expanded into stronger harnesses, evals, and runtime surfaces

## Next Build Targets

The next layer I want to make more explicit in public repos:

<!-- portfolio-next-targets:start -->

- compact agent harness lab with repeatable tasks and pass/fail checks
- stronger trace and evaluation surfaces around tool use
- more examples that show how CLI products fit into actual operator workflows

<!-- portfolio-next-targets:end -->

If you are working on AI agents, evaluation, automation, or developer tooling, this is the direction I am building toward.