#!/usr/bin/env python3
"""
scripts/enforce_all_rules.py

Automate enforcement of all Cursor/MCP rules by querying the MCP JSON-RPC endpoint for tools
starting with "enforce_rule_" and calling their HTTP enforcement endpoints.
"""
import sys
import requests

RPC_URL = "http://localhost:8000/rpc"
HTTP_URL_TEMPLATE = "http://localhost:8000/rules/enforce/{rule}"


def list_rules():
    """List all enforce_rule_* offerings via JSON-RPC."""
    payload = {"jsonrpc": "2.0", "method": "listOfferings", "params": {}, "id": 1}
    resp = requests.post(RPC_URL, json=payload)
    resp.raise_for_status()
    data = resp.json()
    offerings = data.get("result", {}).get("offerings", [])
    return [o for o in offerings if o.startswith("enforce_rule_")]


def enforce_rule(tool_name: str):
    """Call the HTTP enforcement endpoint for a given tool_name."""
    rule = tool_name[len("enforce_rule_"):]
    url = HTTP_URL_TEMPLATE.format(rule=rule)
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def main():
    rules = list_rules()
    if not rules:
        print("No enforce_rule_* offerings found.")
        sys.exit(1)

    for tool_name in rules:
        rule = tool_name[len("enforce_rule_"):]
        print(f"Enforcing {rule}...")
        try:
            result = enforce_rule(tool_name)
            print(result)
        except Exception as e:
            print(f"Failed to enforce {rule}: {e}")
    sys.exit(0)


if __name__ == "__main__":
    main() 