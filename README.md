# AUTOM8LABS Connector Skills

Skills that help **Claude, ChatGPT and Codex** operate AUTOM8LABS MCP Connectors
efficiently: choose the right tools, scope queries, batch operations and verify
results. Available tools depend on the connected application and connector.

## Skills

| Skill | Application |
|---|---|
| [revit-connector](revit/skills/revit-connector/SKILL.md) | Revit |
| [autocad-connector](autocad/skills/autocad-connector/SKILL.md) | AutoCAD |
| [navisworks-connector](navisworks/skills/navisworks-connector/SKILL.md) | Navisworks |
| [microstation-connector](microstation/skills/microstation-connector/SKILL.md) | MicroStation |
| [dynamo-connector](dynamo/skills/dynamo-connector/SKILL.md) | Dynamo in Revit or Sandbox |
| [3dsmax-connector](3dsmax/skills/3dsmax-connector/SKILL.md) | 3ds Max |
| [grasshopper-connector](grasshopper/skills/grasshopper-connector/SKILL.md) | Grasshopper in Rhino or Rhino.Inside.Revit |
| [unreal-connector](unreal/skills/unreal-connector/SKILL.md) | Unreal Editor |

## Install

Install and connect the relevant [AUTOM8LABS connector](https://autom8labs.io),
then add its skill to your client.

- **Claude Code:** use the plugin marketplace.
- **Claude Desktop:** upload an individual skill ZIP.
- **Codex CLI/IDE:** run `python3 scripts/install_codex.py` from a clone of this repo.
- **ChatGPT desktop:** load the combined plugin locally where supported.

[Setup instructions](docs/installation.md) ·
[Download ZIPs](https://github.com/AUTOM8LABS/mcp-connector-skills/releases/latest)

After installation, select the skill and try:

> Identify the connected application and active document. Summarise the session
> without changing anything.

## Build and check

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
python3 scripts/package_skills.py --output dist/skills
python3 scripts/package_plugin.py --output dist/plugin
```

Use `py -3` on Windows. Each build needs an empty output directory.
[Check a live connection](docs/smoke-tests.md).

[autom8labs.io](https://autom8labs.io) · info@autom8labs.io
