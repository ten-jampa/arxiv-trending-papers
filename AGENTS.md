# Agent Instructions

## Project Stage

This repository is currently in the specification and architecture-shaping stage.

Do not jump straight to a full E2E product. First preserve and update the artifacts in `_docs/`.

## Change Discipline

- Keep changes small and artifact-gated.
- Start implementation from `_docs/spec.md` and `_docs/solution-shape.md`.
- Update docs when implementation reality changes.
- Do not add external paid services or secrets.
- Do not add deployment until local CLI usefulness is proven.

## Verification Expectations

For documentation-only changes:

- Check file presence.
- Check Markdown is readable.
- Review git diff.

For code changes once they exist:

- Run tests.
- Run a CLI smoke check.
- Include the exact command output in the handoff.

## Side-Effect Boundaries

Allowed without extra approval:

- Local files in this repository.
- Local tests and static checks.
- Public unauthenticated GET requests for research APIs.

Ask before:

- Pushing to GitHub.
- Creating cron jobs.
- Writing to Obsidian.
- Posting/sending scheduled messages.
- Adding paid APIs or credentials.
- Deploying anything.
