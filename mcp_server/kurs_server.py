"""Kurs-Server: ein eigener MCP-Server mit den Stundenplan-Tools.

MCP (Model Context Protocol) ist ein Standard-Stecker für Tools. Der Server ist ein
eigenes Programm. Jeder MCP-Client kann seine Tools nutzen: unser ADK-Agent,
aber genauso Claude Desktop, Claude Code oder andere Agenten.

Der Agent startet dieses Programm selbst und spricht über stdio mit ihm
(stdio = Standard-Ein-/Ausgabe, also wie über eine Textleitung). Deshalb hier nie print().
"""

import csv
from datetime import date
from pathlib import Path

from mcp.server.mcpserver import MCPServer

DATEN = Path(__file__).parents[1] / "daten"

server = MCPServer("Kurs-Server")


# @server.tool() macht aus einer normalen Python-Funktion ein MCP-Tool.
# Name, Docstring und Parameter sieht der Client automatisch.
@server.tool()
def naechster_kurstag() -> dict:
    """Gibt den heutigen oder nächsten Kurstag zurück (Datum, Zeit, Raum, Thema)."""
    heute = date.today().isoformat()
    with open(DATEN / "stundenplan.csv", encoding="utf-8") as f:
        for zeile in csv.DictReader(f, delimiter=";"):
            if zeile["datum"] >= heute:
                return {"heute": heute, "kurstag": zeile}
    return {"heute": heute, "kurstag": None}


@server.tool()
def stundenplan() -> list:
    """Gibt den ganzen Stundenplan des CAS zurück, alle Kurstage mit Raum und Thema."""
    with open(DATEN / "stundenplan.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


if __name__ == "__main__":
    server.run()  # Standard ist transport="stdio"
