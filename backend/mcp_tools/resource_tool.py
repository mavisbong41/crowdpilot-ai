from mcp_tools.mongodb_tool import get_resource_template


async def get_resource_template_by_severity(
    severity: str
):
    result = await get_resource_template(
        severity
    )

    if not result:
        return {
            "template_found": False,
            "severity": severity
        }

    if isinstance(result, list):
        template = result[0]
    else:
        template = result

    return {
        "template_found": True,
        "severity": template.get("severity"),
        "security_staff": template.get("security_staff", 0),
        "medical_teams": template.get("medical_teams", 0),
        "traffic_controllers": template.get("traffic_controllers", 0)
    }