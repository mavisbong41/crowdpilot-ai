from mcp_tools.mongodb_tool import (
    get_incident_playbook
)


async def get_playbook_by_incident_type(
    incident_type: str
):

    result = await get_incident_playbook(
        incident_type
    )

    # MCP 返回空
    if not result:
        return {
            "playbook_found": False,
            "incident_type": incident_type
        }

    # MCP 返回结果格式可能是 list
    if isinstance(result, list):
        playbook = result[0]
    else:
        playbook = result

    return {
        "playbook_found": True,
        "incident_type": playbook.get("incident_type"),
        "severity": playbook.get("severity"),
        "actions": playbook.get("actions", []),
        "required_units": playbook.get("required_units", [])
    }