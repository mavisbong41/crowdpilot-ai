import json
import re

from mcp_tools.mongodb_mcp_client import mongodb_mcp_client


# ==========================
# INTERNAL HELPER
# ==========================

def _parse_mcp_result(result) -> list:
    if not hasattr(result, "content") or not result.content:
        return []

    for block in result.content:
        text = getattr(block, "text", "")
        if not text:
            continue

        match = re.search(
            r"<untrusted-user-data-[^>]+>\s*(\[.*?\])\s*</untrusted-user-data-[^>]+>",
            text,
            re.DOTALL
        )
        json_str = match.group(1) if match else None
        if not json_str:
            continue

        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                return data
            return [data]
        except (json.JSONDecodeError, TypeError):
            continue

    return []


# ==========================
# MCP TOOLS FOR ADK AGENTS
# ==========================

async def get_historical_events() -> list:
    """Return historical crowd events as a plain list of dicts."""
    result = await mongodb_mcp_client.call_tool(
        "find",
        {
            "database": "crowdpilot",
            "collection": "events",
        },
    )
    return _parse_mcp_result(result)


async def get_active_incidents() -> list:
    """Return active incidents as a plain list of dicts."""
    result = await mongodb_mcp_client.call_tool(
        "find",
        {
            "database": "crowdpilot",
            "collection": "incidents",
        },
    )
    return _parse_mcp_result(result)


async def get_incident_playbook(incident_type: str) -> list:
    """
    Return playbook documents for the given incident type.

    Returns a list of dicts (empty list if none found).
    ADK agents must receive a JSON-serialisable value, so we
    always parse the raw CallToolResult here.
    """
    result = await mongodb_mcp_client.call_tool(
        "find",
        {
            "database": "crowdpilot",
            "collection": "incident_playbooks",
            "filter": {"incident_type": incident_type},
        },
    )

    parsed = _parse_mcp_result(result)

    print("\n===== PLAYBOOK RESULT =====")
    print(parsed)
    print("===========================\n")

    return parsed


async def save_operation_plan(plan: dict) -> dict:
    """
    Persist an operation plan to MongoDB.

    Returns a confirmation dict so the ADK agent receives
    a JSON-serialisable acknowledgement.
    """
    result = await mongodb_mcp_client.call_tool(
        "insert-many",
        {
            "database": "crowdpilot",
            "collection": "operation_plans",
            "documents": [plan],
        },
    )
    # The write result is informational; return a simple ack
    return {"saved": True, "collection": "operation_plans"}


# ==========================
# WRAPPER USED BY mission_runtime
# ==========================

class MongoMCPWrapper:
    async def find(self, collection: str, filter: dict | None = None) -> list:
        result = await mongodb_mcp_client.call_tool(
            "find",
            {
                "database": "crowdpilot",
                "collection": collection,
                "filter": filter or {},
            },
        )
        print("\n===== RAW MCP RESULT =====")
        print(result)
        parsed = _parse_mcp_result(result)
        print("===== PARSED =====")
        print(parsed)
        print("====================\n")
        return parsed

    async def insert_one(self, collection: str, document: dict):
        result = await mongodb_mcp_client.call_tool(
            "insert-many",
            {
                "database": "crowdpilot",
                "collection": collection,
                "documents": [document],
            },
        )
        return result

    async def update_one(self, collection: str, filter: dict, update: dict):
        result = await mongodb_mcp_client.call_tool(
            "update-many",
            {
                "database": "crowdpilot",
                "collection": collection,
                "filter": filter,
                "update": {"$set": update},
                "upsert": False,
            },
        )
        return result

async def get_resource_template(severity: str):
    result = await mongodb_mcp_client.call_tool(
        "find",
        {
            "database": "crowdpilot",
            "collection": "resource_templates",
            "filter": {
                "severity": severity
            }
        }
    )

    parsed = _parse_mcp_result(result)

    if not parsed:
        return None

    return parsed[0]

mongodb_mcp = MongoMCPWrapper()