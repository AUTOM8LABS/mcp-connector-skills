# Installation

Connect the relevant AUTOM8LABS connector to your client first. Each skill folder
contains `SKILL.md` and `agents/openai.yaml`; keep both files together.

## Claude Code

```text
/plugin marketplace add AUTOM8LABS/mcp-connector-skills
/plugin install revit-connector@autom8labs-mcp-skills
```

Replace `revit-connector` with the skill you need. Invoke the marketplace skill
with `/revit-connector:revit-connector`.

For manual installation, copy `revit/skills/revit-connector/` into
`~/.claude/skills/` or your project's `.claude/skills/`, then use `/revit-connector`.
[Claude Code documentation](https://code.claude.com/docs/en/skills).

## Claude Desktop / claude.ai

Download an individual ZIP, such as `revit-connector.zip`, from
[releases](https://github.com/AUTOM8LABS/mcp-connector-skills/releases/latest).
Upload it through **Customize > Skills** and enable it.
[Claude's skill guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## Codex CLI / IDE

With Python 3.10+ installed:

```sh
git clone https://github.com/AUTOM8LABS/mcp-connector-skills
cd mcp-connector-skills
python3 scripts/install_codex.py --dry-run
python3 scripts/install_codex.py
```

Use `py -3` on Windows. The default destination is `~/.agents/skills` for the
current OS user. Options:

| Option | Effect |
|---|---|
| `--skill revit-connector` | Install one skill; repeat to select several |
| `--dest "path/to/project/.agents/skills"` | Install into a project |
| `--dry-run --update` | Preview an update |
| `--update` | Replace unchanged installer-owned copies, retaining ZIP backups |

The installer preserves local customizations and unmanaged skills. Select
`$revit-connector` in Codex; start a fresh session if it has not appeared.

## ChatGPT desktop

Download and unzip `autom8labs-operator-skills.zip` from
[releases](https://github.com/AUTOM8LABS/mcp-connector-skills/releases/latest).
Where local plugins are supported, ask `@plugin-creator` to register the extracted
`autom8labs-operator-skills/` folder. Select `@revit-connector` in a fresh chat.
[OpenAI skills](https://learn.chatgpt.com/docs/build-skills) ·
[Plugin setup](https://developers.openai.com/plugins/build/plugins).

This plugin is available for local installation. It has no OpenAI directory
listing for ChatGPT web/mobile. Your session must be able to reach the connector;
installing skill files does not connect a cloud session to a Windows application.

## Connect to the application

Use the bridge path supplied by your installed connector. For example, with
native Windows Revit:

```powershell
codex mcp add AUTOM8LABS_Revit -- "C:/ProgramData/AUTOM8LABS/MCPConnector/Bridge/MCPConnector.Bridge.exe"
codex mcp list
```

For Claude Code, replace `codex mcp add` with `claude mcp add`. Other connectors
use their own bridge or editor registry. Windows and WSL maintain separate
client configurations; use paths for the environment running your client.
[Codex MCP setup](https://learn.chatgpt.com/docs/extend/mcp) ·
[Claude MCP setup](https://code.claude.com/docs/en/mcp).

Select the skill and ask it to identify the connected application and active
document without editing anything. Confirm an actual tool response. If the
connection fails, check the connector, configured path and exposed tools.
