# Check a live connection

Select the installed skill and run the matching read-only check. Record the
client, application and connector versions alongside the result.

| Application | Check | Useful tools |
|---|---|---|
| Revit | Active document and element count | `get_session_info`, `get_document_info`, `get_element_count` |
| AutoCAD | Active drawing and units | `get_drawing_info` |
| Navisworks | Loaded files and existing clash tests | `get_model_info`, `list_models`, `list_clash_tests` |
| MicroStation | Active model, units and element count | `get_model_info`, `count_elements` |
| Dynamo | Graph structure and run mode, without evaluating | `ping`, bounded `get_graph_state` |
| 3ds Max | Scene units and capabilities | `get_scene_info`, `get_host_capabilities` |
| Grasshopper | Definition summary, without solving or baking | `get_definition_summary`, bounded `get_canvas_state` |
| Unreal | Current level and connector status | Registry discovery, `MCPConnectorTools.ping`, `ArchvizLevelTools.get_level_summary` |

Tool names and arguments must match the connected session's schemas. A passing
check identifies the actual application/document and returns the requested data.

For write tests, use an authorized disposable document. Make one small change,
read back the affected values, and check units and identifiers. For a graph,
verify the evaluated terminal output; for a render, inspect the completed job
and output. Check partial failures and actual state before retrying a write.

The Python tests cover packaging and installation. Live checks establish whether
a particular client can reach and operate the application.
