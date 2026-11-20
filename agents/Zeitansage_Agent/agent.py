"""Zeitansage_Agent: Claude Haiku via LiteLLM in Google ADK, mit einem Python-Tool."""

import math
from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext


def aktuelle_uhrzeit(tool_context: ToolContext) -> dict:
    """Gibt die aktuelle Uhrzeit in der Schweiz zurück, mit einem Hinweis zum Kurstag."""
    jetzt = datetime.now(ZoneInfo("Europe/Zurich"))
    kursende = jetzt.replace(hour=17, minute=15, second=0, microsecond=0)

    if jetzt < kursende:
        rest_minuten = math.ceil((kursende - jetzt).total_seconds() / 60)
        stunden = rest_minuten // 60
        minuten = rest_minuten % 60
        hinweis = f"CAS Kurstag: Dann musst du noch maximal {stunden} Stunden und {minuten} Minuten durchhalten."
    else:
        hinweis = "Feierabend!"

    ansage = f"Es ist {jetzt:%H:%M} Uhr. {hinweis}"

    # tool_context.actions.skip_summarization = True

    # --- DEMO: Entferne das # vor der Zeile oben, dann wird das Tool-Ergebnis
    # NICHT an Claude geschickt.
    # Normalerweise geht das Tool-Ergebnis zurück an Claude, und Claude
    # formuliert daraus die Antwort (zweite Modellrunde).
    # Ohne # zeigt ADK das Ergebnis direkt an, und Claude sieht es nie.
    # Nach jeder Änderung den Server neu starten.
    # -------------------------------------------------------------------------

    return {"status": "ok", "ansage": ansage}


root_agent = Agent(
    name="Zeitansage_Agent",
    model=LiteLlm(model="anthropic/claude-haiku-5-5"),
    description="Sagt die aktuelle Uhrzeit an und wie lange der Kurstag noch dauert.",
    instruction=(
        "Du bist ein freundlicher Assistent in einem Weiterbildungskurs. "
        "Antworte kurz und auf Deutsch. "
        "Wenn nach Datum, Uhrzeit oder Kursende gefragt wird, rufe das Tool "
        "aktuelle_uhrzeit auf und gib dessen Feld 'ansage' mit einer kleinen total lustigen Variation wieder."
    ),
    tools=[aktuelle_uhrzeit],
) 
