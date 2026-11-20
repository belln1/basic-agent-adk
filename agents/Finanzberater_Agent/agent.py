"""Finanzberater_Agent: ein Loop aus Berater und Compliance-Prüfer.
Harte Regeln prüft Python (after_agent_callback), weiche Regeln prüft ein LLM."""

import re

from google.adk.agents import Agent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import exit_loop


# ---------------------------------------------------------------- Harte Regeln (Python)

def regeln_pruefen(callback_context: CallbackContext) -> None:
    """after_agent_callback: läuft NACHDEM der Berater seinen Entwurf geschrieben hat."""
    entwurf = callback_context.state.get("entwurf", "")
    verstoesse = []

    if len(entwurf.split()) > 80:
        verstoesse.append(f"zu lang ({len(entwurf.split())} statt höchstens 80 Wörter)")
    if "risiko" not in entwurf.lower():
        verstoesse.append("das Wort 'Risiko' fehlt")
    if re.search(r"\d+\s?%", entwurf):
        verstoesse.append("enthält eine Prozentzahl (wirkt wie ein Renditeversprechen)")

    # Das Ergebnis kommt in den State. Der Prüfer liest es dort als {regelcheck}.
    callback_context.state["regelcheck"] = "; ".join(verstoesse) if verstoesse else "OK"
    return None  # None heisst: die Antwort des Beraters bleibt unverändert


# ---------------------------------------------------------------- Agenten

berater = Agent(
    name="Berater_Agent",
    model=LiteLlm(model="anthropic/claude-haiku-5-5"),
    instruction=(
        "Du bist ein begeisterter Kundenberater einer Schweizer Bank. "
        "Beantworte die Kundenfrage auf Deutsch, motivierend und mit konkreten Zahlen.\n"
        "Kritik der Compliance zur letzten Version (leer in Runde 1): {kritik?}\n"
        "Wenn es Kritik gibt, überarbeite deinen Text so, dass alle Punkte erfüllt sind. "
        "Gib nur den Antworttext an den Kunden aus."
    ),
    output_key="entwurf",
    after_agent_callback=regeln_pruefen,
)

pruefer = Agent(
    name="Pruefer_Agent",
    model=LiteLlm(model="anthropic/claude-sonnet-5-5"),
    instruction=(
        "Du bist die Compliance-Abteilung einer Schweizer Bank und prüfst diesen Entwurf:\n"
        "{entwurf}\n\n"
        "Ergebnis der automatischen Regelprüfung: {regelcheck}\n\n"
        "Prüfe zusätzlich: kein Renditeversprechen, keine persönliche Anlageempfehlung "
        "ohne Beratungsgespräch, ein Hinweis auf ein Beratungsgespräch ist enthalten.\n"
        "Wenn die Regelprüfung OK ist und du keinen Verstoss findest: rufe exit_loop auf.\n"
        "Sonst: nenne die Verstösse in einer kurzen Liste, ohne den Text selbst umzuschreiben."
    ),
    tools=[exit_loop],
    output_key="kritik",
)

root_agent = LoopAgent(
    name="Finanzberater_Agent",
    sub_agents=[berater, pruefer],
    max_iterations=3,  # Notbremse, falls sich die beiden nie einig werden
)
