"""Kurs_MCP: ein Agent, der seine Tools nicht selbst hat, sondern von einem MCP-Server holt.

Beim Kurs_Assistent stehen die Tools als Python-Funktionen in derselben Datei.
Hier steht kein einziges Tool im Code. Der Agent startet den Kurs-Server
(mcp_server/kurs_server.py), fragt ihn "welche Tools hast du?" und benutzt sie.
"""

import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

SERVER = Path(__file__).parents[2] / "mcp_server" / "kurs_server.py"

# McpToolset = alle Tools eines MCP-Servers als Paket.
# StdioServerParameters = mit welchem Befehl der Server gestartet wird,
# hier: dasselbe Python wie für den Agenten, mit der Server-Datei.
kurs_server = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(command=sys.executable, args=[str(SERVER)]),
        timeout=30,  # Sekunden, die der Server zum Starten hat
    ),
)

root_agent = Agent(
    name="Kurs_MCP",
    model=LiteLlm(model="anthropic/claude-haiku-5-5"),
    instruction=(
        "Du beantwortest Fragen zum Stundenplan eines CAS an der ZHAW, kurz und auf Deutsch. "
        "Nutze dafür die Tools des Kurs-Servers."
    ),
    tools=[kurs_server],
)
