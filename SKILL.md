---
name: managing-libraries-is-a-drag
description: Use this skill automatically and without exception whenever ANY new library, package, or dependency that requires third-party license documentation is added to the project, whether explicitly requested by the user or introduced automatically during code modification and package management (e.g., package.json, requirements.txt, Cargo.toml updates).
---

# Managing Libraries is a Drag

## Goal
To document ALL newly added libraries that require third-party license disclosure across any ecosystem, ensuring `docs/using-library/lib-WH.md` serves as a complete and flawless tracking sheet for licensing compliance.

## Instructions
1. Identify ALL library names and their ecosystems from the user's request OR from the files modified during the turn (e.g., package.json, Cargo.toml, requirements.txt). You must scan for every single added dependency that requires third-party license tracking, including minor utilities and sub-dependencies.
2. Check `references/rules.md` to see if the ecosystem is supported by the lookup script.
3. Autonomously draft the Description and Rationale for each identified library based on the context to minimize user typing.
4. Present the drafted Descriptions and Rationales to the user and wait for confirmation. Do NOT proceed without explicit user approval ("Yes").
5. Locate the repository root folder where this `SKILL.md` and the `scripts/` directory reside. Once confirmed, run the script for each supported ecosystem:
   - Command: `python PATH/to/scripts/fetch-lib-info.py --system <ecosystem> --name <name>` (Append `--version <version>` if specified).
6. Parse the JSON returned by the script. If `error` is not null, `api_supported` is false, or data is missing, use web search to find the correct version and license.
7. Read `docs/using-library/lib-WH.md`. Insert or update all library entries under the correct section in alphabetical order, strictly following the format defined in `references/rules.md`.

## Constraints
- Do not omit any dependency that requires third-party license documentation. Ensuring 100% compliance coverage is your absolute top priority.
- Always get user confirmation on the Description and Rationale before making file modifications.
- Refer to `references/rules.md` for all supported ecosystems and the mandatory output structure.