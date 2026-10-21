---
name: rea-tool-design
description: >
  Design or change REA investigation tools, CLI/MCP contracts, provider capabilities, and Evidence
  semantics.
metadata:
  source: cristianoleamiranda-dotcom/Rae
  source-path: agent/skills/rea-tool-design/SKILL.md
  source-commit: 4269e1758c39a5f4431ce47092e09bf555595cc5
  category: reverse-engineering
  status: ok
---
# REA tool design

Use the [tool-design guide](../../../docs/tool-design.md) for tool boundaries,
contract semantics, provider ownership, and discoverability. Inspect the current
contract and nearest existing tool relevant to the analyst question; source,
documentation, and live catalogs may describe different versions.

For a design request, return the proposed boundary, input/result shape, Evidence
semantics, nearest alternative, and verification approach. Implement when
requested, preserving the user's scope and existing authorization.

For implementation or verification, consult [testing](../../../docs/testing.md)
for the affected consumer and provider lanes, and
[contributing](../../../CONTRIBUTING.md) for generated-file ownership. Read
provider/workflow guides only as the task requires.
