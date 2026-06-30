# Managing Libraries is a Drag - Rules and Reference

## Supported API Ecosystems
The `fetch-lib-info.py` script natively supports the following systems via the deps.dev API. If the target library belongs to one of these, always attempt script execution first:
- npm
- cargo
- pypi
- go
- rubygems
- maven
- nuget

For any other systems (e.g., custom, c, lua), the API is not supported. The agent must bypass the script or handle failures gracefully by using web search to find the exact version and license.

## Output Format for docs/using-library/lib-WH.md
Every entry written to the warehouse file must strictly adhere to the following Markdown format. Do not alter the keys or structure:

```markdown
## [Language]
- **[Library Name]:** {Library Name}
- **Description:** {Description}
- **Rationale:** {Rationale}
- **Version:** {Version}
- **License:** {License}
```