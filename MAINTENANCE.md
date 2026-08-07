# Product Maintenance Roadmap

This profile is maintained as an AI Agent / Harness Engineering product portfolio. Roadmap items move only when a repository ships operator-visible evidence: a runnable command, an inspectable artifact, or an automated quality check.

## Shipped Foundation

- `sushi-agent`: embeddable TypeScript and Rust runtime surface for providers, skills, MCP, and local tools.
- `agent-meeting-notes`: working CLI from long audio to transcript, summary, structured notes, and quality checks.
- `xhs-content-agent`: human-reviewed CLI from raw idea to draft, calendar, publish package, and strict checks.
- `dyrc9`: machine-readable portfolio manifest, generated README sections, schema validation, and CI drift checks.

The common product contract is:

```text
source input -> staged processing -> inspectable artifact -> quality gate -> human or system decision
```

## Now: Prove Repeatable Harness Evaluation

Build one compact evaluation slice around an existing product before starting another broad framework.

Recommended first target: `agent-meeting-notes`, using a deterministic transcript fixture so the evaluation does not require network access or model credentials.

Definition of done:

- one versioned task fixture with explicit inputs and expected outcomes
- one command that runs the fixture locally
- a durable JSON result containing task version, checks, pass/fail status, and timing
- at least one passing and one intentionally failing test case
- CI coverage for the runner and result schema
- a README example showing the command, artifact, and failure diagnosis

## Next: Make Runs Comparable

Once the first evaluation slice is stable:

- add a run identifier and configuration fingerprint to evaluation artifacts
- retain normalized traces without secrets or raw credentials
- compare two result artifacts and explain changed checks
- document how an operator promotes a fixture change intentionally

Completion signal: a contributor can reproduce a run and identify why two runs differ without reading implementation code.

## Later: Extract Shared Harness Primitives

Extract a separate `agent-harness-lab` only after two products need the same runner or result contract. Candidate shared primitives:

- versioned task definitions
- subprocess and tool-call adapters
- transcript and trace normalization
- deterministic assertions and rubric scoring
- result comparison and regression summaries

This avoids building a generic harness before the portfolio has concrete reuse pressure.

## Maintenance Cadence

### Weekly

- ship one operator-visible improvement in an active product
- add or strengthen one regression check
- verify that profile claims link to current product evidence
- capture one failure mode or tradeoff in product documentation

### Monthly

- run every documented quickstart and proof command
- review active-product status, repository descriptions, topics, and pins
- archive roadmap items that no longer support the harness-engineering direction
- promote only shipped work into the profile narrative

## Scope Guardrails

- Prefer reproducible workflows over screenshot-only demos.
- Keep artifacts inspectable, portable, and safe to retain.
- Require human review for publishing or other external side effects.
- Do not build engagement manipulation, CAPTCHA bypass, policy evasion, or spam automation.
