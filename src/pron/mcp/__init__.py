"""The MCP surface (spec 14): a server over stdio that mounts several worlds and answers
agents with JSON, never with sentences.

Only `pron.mcp.server` imports the MCP SDK (`pip install pron[mcp]`, spec 14 §1); the read
plane (spec 14 §2, §3) and the tool table are plain library, testable without it.
"""
