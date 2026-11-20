"""Kurs_Workflow (ein fest programmierter Ablauf): gleiche Aufgabe wie Kurs_Assistent,
aber mit Sequential, Parallel und State statt einem Agenten, der selbst entscheidet.

Hinweis zu ADK 2.x: SequentialAgent, ParallelAgent und LoopAgent sind als veraltet markiert
(Warnung im Terminal), funktionieren aber. Der Nachfolger heisst Workflow, ein Graph aus Kanten:

    from google.adk import Workflow
    from google.adk.workflow import JoinNode

    join = JoinNode(name="sammeln")
    root_agent = Workflow(
        name="Kurs_Workflow",
        edges=[
            ("START", kurstag_agent, (wetter_agent, mensa_agent)),  # erst Kurstag, dann beide parallel
            ((wetter_agent, mensa_agent), join),                    # warten, bis beide fertig sind
            (join, briefing_agent),
        ],
    )

Wichtiger Unterschied: Im Workflow sehen die Agenten nach START NICHT den Gesprächsverlauf,
sondern nur die Ausgabe ihres Vorgängers (mode="single_turn"). Ein E-Mail-Wunsch aus der
ersten Nachricht ginge dort verloren, ausser man legt ihn vorher in den State.
Die Agent-Objekte unten lassen sich nicht 1:1 wiederverwenden: Für einen Workflow eigene anlegen."""

from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

# Gleiche Tools und Callback wie beim Kurs_Assistent, nur anders zusammengesetzt.
from Kurs_Assistent.agent import (
    email_entwurf, empfaenger_pruefen, mensa_wochenmenue, naechster_kurstag, wetter_mittag,
)

HAIKU = LiteLlm(model="anthropic/claude-haiku-5-5")    # günstig, für einfache Schritte
SONNET = LiteLlm(model="anthropic/claude-sonnet-5-5")  # stärker, für das Interpretieren

# Schritt 1: Kurstag holen. output_key legt die Antwort im State unter "kurstag" ab.
kurstag_agent = Agent(
    name="Kurstag_Agent",
    model=HAIKU,
    instruction="Rufe naechster_kurstag auf und gib Datum, Zeit, Raum und Thema in einer Zeile zurück.",
    tools=[naechster_kurstag],
    output_key="kurstag",
)

# Schritt 2a und 2b laufen gleichzeitig. {kurstag} wird aus dem State eingesetzt.
wetter_agent = Agent(
    name="Wetter_Agent",
    model=HAIKU,
    instruction="Kurstag: {kurstag}\nRufe wetter_mittag mit dem Datum des Kurstags auf "
                "und gib die Werte in einer Zeile zurück.",
    tools=[wetter_mittag],
    output_key="wetter",
)

mensa_agent = Agent(
    name="Mensa_Agent",
    model=HAIKU,
    instruction="Rufe mensa_wochenmenue auf. Antworte ausschliesslich mit dem Rohtext aus dem Tool, "
                "ohne Überschrift und ohne Kommentar.",
    tools=[mensa_wochenmenue],
    output_key="menue",
)

recherche = ParallelAgent(name="Recherche", sub_agents=[wetter_agent, mensa_agent])

# Schritt 3: Das stärkere Modell liest alles aus dem State und schreibt das Briefing.
briefing_agent = Agent(
    name="Briefing_Agent",
    model=SONNET,
    instruction=(
        "Schreibe ein kurzes Briefing auf Deutsch für den Kurstag.\n"
        "Kurstag: {kurstag}\nWetter um 12 Uhr: {wetter}\nMensa-Rohtext: {menue}\n"
        "Nenne Raum und Thema, sag klar ob man einen Schirm braucht, und such aus dem "
        "Rohtext die Gerichte dieses Wochentags heraus. "
        "Wenn in der Anfrage eine E-Mail gewünscht ist, nutze email_entwurf (ohne Angabe an 'master')."
    ),
    tools=[email_entwurf],
    before_tool_callback=empfaenger_pruefen,
    # include_contents="none",

    # --- DEMO: Entferne das # vor der Zeile oben, dann sieht der Briefing_Agent
    # nur noch seine Instruktion mit {kurstag}, {wetter}, {menue} und die letzte
    # Nachricht davor (vom Mensa- oder Wetter-Agenten), aber nicht mehr die Frage.
    # Achtung: Beim ERSTEN Agenten bringt das nichts, denn seine "letzte Nachricht
    # davor" IST die Frage der Person. Darum hilft es nicht gegen den Katzenwitz-Test.
    # Normalerweise bekommt er den ganzen Gesprächsverlauf mit: die Frage der Person
    # und die Antworten der anderen Agenten. Ohne # weiss er nicht mehr, ob jemand
    # eine E-Mail wollte. Test: "Briefing für den nächsten Kurstag, bitte per Mail an mich."
    # Nach jeder Änderung den Server neu starten.
    # -------------------------------------------------------------------------
)

root_agent = SequentialAgent(
    name="Kurs_Workflow",
    sub_agents=[kurstag_agent, recherche, briefing_agent],
)
