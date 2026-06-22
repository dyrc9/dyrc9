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
| [sushi-agent](https://github.com/dyrc9/sushi-agent) | TypeScript + Rust runtime for embedding providers, skills, MCP, and fast local tools into existing systems. | Core runtime bet |
| [agent-meeting-notes](https://github.com/dyrc9/agent-meeting-notes) | Long-audio transcription and meeting-notes harness with chunking, structured outputs, and exportable artifacts. | Working CLI product |
| [xhs-content-agent](https://github.com/dyrc9/xhs-content-agent) | Human-reviewed content pipeline for Xiaohongshu / RedNote drafts, calendars, and publish packages. | Working CLI product |
| [dyrc9.github.io](https://github.com/dyrc9/dyrc9.github.io) | Personal site and long-term public surface for demos, notes, and portfolio framing. | Public narrative layer |

## Supporting Repositories

These are relevant because they reinforce the engineering foundation behind the product work:

| Repository | Why it matters |
| --- | --- |
| [console-chat-gpt](https://github.com/dyrc9/console-chat-gpt) | Early CLI experiments around chat APIs and terminal interaction patterns. |
| [cwym](https://github.com/dyrc9/cwym) | Networking and message-oriented systems practice. |
| [CS353Project2](https://github.com/dyrc9/CS353Project2) | Linux kernel lab work and low-level systems exposure. |
| [Kitsune_prp](https://github.com/dyrc9/Kitsune_prp) | Security and intrusion-detection related exploration. |

Older forks and course repositories are being cleaned up so the profile stays product-focused.

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

## Next Build Targets

The next layer I want to make more explicit in public repos:

- a compact agent harness lab with repeatable tasks and pass/fail checks
- stronger trace and evaluation surfaces around tool use
- more examples that show how these CLIs fit into actual operator workflows

If you are working on AI agents, evaluation, automation, or developer tooling, this is the direction I am building toward.
