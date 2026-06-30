# Operation Rules

This document defines the configuration and operational rules for the `managing-libraries-is-a-drag` skill. The configuration block below is parsed dynamically by the underlying Python scripts.

```yaml
warehouse_path: "docs/using-library/lib-WH.md"
license_path: "NOTICE.md"
deny_licenses:
  - "AGPL"
  - "GPL"
  - "Unknown"
ignore_packages:
  - "tailwindcss"
  - "postcss"
format_template: |
  ## [Language]
  - **[Library Name]:** {Library Name}
  - **Description:** {Description}
  - **Rationale:** {Rationale}
  - **Version:** {Version}
  - **License:** {License}
```

## Configuration Details

- **warehouse_path**: The destination path for the generated library inventory document.
- **license_path**: The destination path for the third-party license summary.
- **deny_licenses**: A strict blocklist of SPDX license identifiers. If a dependency resolves to any of these licenses (or returns Unknown), the generation process will immediately halt to ensure compliance.
- **ignore_packages**: A list of essential packages (e.g., build tools, CSS frameworks) that must be protected and never uninstalled during the automated cleanup process, even if they appear unused in static analysis.
- **format_template**: The markdown structure used to generate individual library entries. Do not modify the bracketed/braced variables (e.g., `{Version}`, `[Language]`) as they are mapped directly by the script.