"""Kurs_Assistent (ein Agent, der selbst entscheidet): Tools, Guardrails per Callbacks und ein E-Mail-Entwurf mit Mensch im Loop."""

import csv
import html
import re
import urllib.parse
import webbrowser
from datetime import date
from pathlib import Path

import httpx
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext
from google.genai import types

DATEN = Path(__file__).parents[2] / "daten"

MENSA_URL = (
    "https://app.food2050.ch/de/zfv/zhaw%2Cstandort-winterthur%2Ccampus-st-georgen-platz/"
    "zhaw-mensa-st-georgen/mittagsverpflegung/menu/weekly"
)

# Empfängerliste: Claude kennt nur die Kürzel (master, tn01, ...), nie die Adressen.
with open(DATEN / "empfaenger.csv", encoding="utf-8") as f:
    EMPFAENGER = {zeile["kuerzel"]: zeile["email"] for zeile in csv.DictReader(f, delimiter=";")}


# ---------------------------------------------------------------- Tools

def naechster_kurstag() -> dict:
    """Liest den Stundenplan und gibt den heutigen oder nächsten Kurstag zurück (Datum, Zeit, Raum, Thema)."""
    heute = date.today().isoformat()
    with open(DATEN / "stundenplan.csv", encoding="utf-8") as f:
        for zeile in csv.DictReader(f, delimiter=";"):
            if zeile["datum"] >= heute:
                return {"heute": heute, "kurstag": zeile}
    return {"heute": heute, "kurstag": None}


def wetter_mittag(datum: str) -> dict:
    """Wetterprognose für Winterthur um 12 Uhr. datum im Format JJJJ-MM-TT (höchstens 14 Tage im Voraus)."""
    antwort = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": 47.50, "longitude": 8.72, "timezone": "Europe/Zurich",
            "start_date": datum, "end_date": datum,
            "hourly": "temperature_2m,precipitation_probability,precipitation,weather_code,wind_gusts_10m",
        },
    ).json()
    stunden = antwort["hourly"]
    i = stunden["time"].index(f"{datum}T12:00")
    return {
        "temperatur_c": stunden["temperature_2m"][i],
        "regenwahrscheinlichkeit_prozent": stunden["precipitation_probability"][i],
        "niederschlag_mm": stunden["precipitation"][i],
        "wettercode": stunden["weather_code"][i],  # 95-99 = Gewitter
        "windboeen_kmh": stunden["wind_gusts_10m"][i],
    }


def mensa_wochenmenue() -> dict:
    """Lädt das Wochenmenü der ZHAW Mensa St. Georgen als Rohtext."""
    seite = httpx.get(MENSA_URL, follow_redirects=True).text
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", seite, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)          # HTML-Tags entfernen
    text = re.sub(r"\s+", " ", html.unescape(text))
    return {"menue_rohtext": text[:2500]}


def email_entwurf(empfaenger: str, betreff: str, text: str) -> dict:
    """Öffnet einen E-Mail-Entwurf in Outlook. empfaenger ist ein Kürzel, z.B. 'master' oder 'tn01'."""
    adresse = EMPFAENGER[empfaenger]
    link = f"mailto:{adresse}?subject={urllib.parse.quote(betreff)}&body={urllib.parse.quote(text)}"
    webbrowser.open(link)
    # Claude erfährt nur das Kürzel, nicht die Adresse. Senden muss der Mensch.
    return {"status": "Entwurf geöffnet, bitte in Outlook prüfen und selbst senden", "empfaenger": empfaenger}


# ---------------------------------------------------------------- Guardrails (Callbacks)

ERLAUBTE_WOERTER = ["cas", "kurs", "raum", "thema", "stundenplan", "unterricht",
                    "wetter", "schirm", "regen", "mensa", "essen", "menü", "mittag", "mail"]


def thema_pruefen(callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None:
    """before_model_callback: läuft VOR jedem Aufruf von Claude."""
    letzte = llm_request.contents[-1]
    eingabe = " ".join(teil.text for teil in letzte.parts if teil.text).lower()
    if not eingabe:  # z.B. ein Tool-Ergebnis, kein Text der Person
        return None
    if any(wort in eingabe for wort in ERLAUBTE_WOERTER):
        return None  # None heisst: weiter zu Claude
    # Eine eigene Antwort heisst: Claude wird gar nicht aufgerufen.
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(
        text="Dafür wurde ich nicht geschaffen. Ich helfe nur bei Fragen rund um den CAS-Kurstag.")]))


def empfaenger_pruefen(tool, args: dict, tool_context: ToolContext) -> dict | None:
    """before_tool_callback: läuft VOR jedem Tool-Aufruf."""
    if tool.name == "email_entwurf" and args.get("empfaenger") not in EMPFAENGER:
        # Ein eigenes Ergebnis heisst: das Tool wird gar nicht ausgeführt.
        return {"status": "blockiert", "grund": f"Erlaubt sind nur: {', '.join(EMPFAENGER)}"}
    return None


# ---------------------------------------------------------------- Agent

root_agent = Agent(
    name="Kurs_Assistent",
    model=LiteLlm(model="anthropic/claude-haiku-5-5"),
    description="Hilft rund um den CAS-Kurstag: Raum, Thema, Wetter, Mensa, E-Mail-Entwurf.",
    instruction=(
        "Du bist der Hilfs-Programmmanger bzw. Assistent eines CAS an der ZHAW. Antworte kurz und auf Deutsch. "
        "Für Raum und Thema nutze naechster_kurstag, für das Wetter wetter_mittag mit dem Datum "
        "des Kurstags, für das Essen mensa_wochenmenue. Im Menü-Rohtext suchst du die Gerichte "
        "des Kurstags heraus. Sag beim Wetter klar, ob man einen Schirm braucht. "
        "Wenn eine E-Mail gewünscht ist, nutze email_entwurf. Ohne Angabe geht sie an 'master'."
    ),
    tools=[naechster_kurstag, wetter_mittag, mensa_wochenmenue, email_entwurf],
    before_model_callback=thema_pruefen,
    before_tool_callback=empfaenger_pruefen,
)
