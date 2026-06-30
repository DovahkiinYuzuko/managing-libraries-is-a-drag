---
name: managing-libraries-is-a-drag
description: Use this skill when a new library or package is added to the project and needs to be documented and tracked in the central library warehouse (docs/using-library/lib-WH.md).
---

# Managing Libraries is a Drag

## Goal
To document newly added libraries across any ecosystem by combining automated API lookups with the agent's file manipulation capabilities, ensuring `docs/using-library/lib-WH.md` is always accurate and ordered.

## Instructions
1. Identify the library name and its ecosystem from the user's request.
2. Check `references/rules.md` to see if the ecosystem is supported by the lookup script.
3. Autonomously draft the Description and Rationale based on the library's context to minimize user typing.
4. Present the drafted Description and Rationale to the user and wait for confirmation. Do NOT proceed without explicit user approval ("Yes").
5. Once confirmed, if the ecosystem is supported, run the script:
   - Command: `python scripts/fetch-lib-info.py --system <ecosystem> --name <name>` (Append `--version <version>` if specified).
6. Parse the JSON returned by the script. If `error` is not null, `api_supported` is false, or data is missing, use web search to find the correct version and license.
7. Read `docs/using-library/lib-WH.md`. Insert or update the library entry under the correct section in alphabetical order, strictly following the format defined in `references/rules.md`.

## Constraints
- Always get user confirmation on the Description and Rationale before making file modifications.
- Refer to `references/rules.md` for all supported ecosystems and the mandatory output structure.