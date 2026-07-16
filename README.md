# AUTOM8LABS MCP Connector Skills

Operator skills for the AUTOM8LABS **MCP Connector** family. A skill is a
markdown playbook your AI client loads alongside the connector - it teaches
the AI to drive the tools efficiently: fewer calls, fewer tokens, the right
tool first time, and honest handling of units, IDs, and destructive
operations.

Skills are optional. The connectors work without them - but with them the AI
wastes far less of your context window and makes fewer mistakes.

| Skill | Product | Host versions |
|---|---|---|
| [`revit-connector`](revit/skills/revit-connector/SKILL.md) | MCP Connector for Revit | Revit 2022–2027 |
| [`autocad-connector`](autocad/skills/autocad-connector/SKILL.md) | MCP Connector for AutoCAD | AutoCAD 2022–2027 |
| [`navisworks-connector`](navisworks/skills/navisworks-connector/SKILL.md) | MCP Connector for Navisworks | Navisworks 2024–2027 |
| [`microstation-connector`](microstation/skills/microstation-connector/SKILL.md) | MCP Connector for MicroStation | MicroStation 2024 |
| [`dynamo-connector`](dynamo/skills/dynamo-connector/SKILL.md) | MCP Connector for Dynamo | Dynamo 3.x (Revit 2025/2026, Sandbox) |
| [`3dsmax-connector`](3dsmax/skills/3dsmax-connector/SKILL.md) | MCP Connector for 3ds Max | 3ds Max 2022–2027 |
| [`grasshopper-connector`](grasshopper/skills/grasshopper-connector/SKILL.md) | MCP Connector for Grasshopper | Rhino 8 / Rhino.Inside Revit |

Skills work with both Free and Pro editions. Each playbook covers the full
tool family, and your AI simply uses whichever tools your edition provides.

---

## Install

### Claude Code

Via the plugin marketplace (recommended - updates with one command):

```
/plugin marketplace add AUTOM8LABS/mcp-connector-skills
/plugin install revit-connector@autom8labs-mcp-skills
```

Or manually - copy the skill folder into your user skills directory:

```powershell
git clone https://github.com/AUTOM8LABS/mcp-connector-skills
Copy-Item -Recurse mcp-connector-skills\revit\skills\revit-connector $HOME\.claude\skills\
```

### Claude Desktop / claude.ai

1. Download this repository (Code → Download ZIP) or clone it.
2. Zip the individual skill folder - e.g. `revit/skills/revit-connector/`
   (the folder containing `SKILL.md`).
3. In Claude: **Settings → Capabilities → Skills → Upload skill** and select
   the zip.

### Cursor

Cursor uses rules rather than skills. Copy the body of the relevant
`SKILL.md` into a project rule:

```powershell
Copy-Item mcp-connector-skills\revit\skills\revit-connector\SKILL.md .cursor\rules\revit-connector.mdc
```

(or paste the content into your project's `AGENTS.md`).

### Other MCP clients

Any client that supports instruction/system files can use these - paste the
`SKILL.md` body into your client's custom-instructions mechanism for the
sessions where you drive the connector.

---

## Prerequisite: the connector itself

Each skill assumes its MCP Connector is installed and wired into your AI
client. The connector installers configure Claude Desktop and Cursor
automatically; for Claude Code add the installed Bridge exe manually, e.g.:

```
claude mcp add AUTOM8LABS_Revit "C:\ProgramData\AUTOM8LABS\MCPConnector\Bridge\MCPConnector.Bridge.exe"
```

The MCP server keys used by the family: `AUTOM8LABS_Revit`,
`AUTOM8LABS_AutoCAD`, `AUTOM8LABS_Navisworks`, `AUTOM8LABS_MicroStation`,
`AUTOM8LABS_3dsMax` (Dynamo and Grasshopper: see each product's docs). The
exact Bridge exe path is shown by each product's in-app status command and
in its documentation.

Product pages, licences, and documentation: [autom8labs.io](https://autom8labs.io)

---

## Support

- Email: info@autom8labs.io
- Website: [autom8labs.io](https://autom8labs.io)

**Made by [AUTOM8LABS](https://autom8labs.io)** - UK-based AI automation,
add-ins and workflow tools for AEC.
