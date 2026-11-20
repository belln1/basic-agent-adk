# CAS-Agentenprojekt (Google ADK über LiteLLM, in Google Colab)

Lernprojekt im Unterricht (ZHAW). Die Teilnehmenden sind keine
Software-Entwickler. Ziel ist, Konzepte zu verstehen, nicht produktiven Code zu schreiben.
Sie arbeiten nur in Google Colab, mit Gemini als Code-Assistent.
Die Sprachmodelle der Agenten kommen über einen OpenAI-kompatiblen Anbieter (OpenRouter).
Diese Datei ist für die Pflege des Repos.

## Inhalt
- `Zeitansage_Agent.ipynb`: ein Agent, ein Tool, `tool_context`, `skip_summarization`-Demo.
- `Finanzberater_Agent.ipynb`: `LoopAgent` (max. 3 Runden) aus Berater und Compliance-Prüfer
  (Tool `exit_loop`). Ein `after_agent_callback` prüft harte Regeln in Python und legt das
  Ergebnis als `regelcheck` in den State. `{kritik?}` = optionaler Platzhalter für Runde 1.
- `README.md`: Anleitung für die Teilnehmenden mit «In Colab öffnen»-Links.
  Die Links zeigen auf `github.com/belln1/basic-agent-adk`, Branch `main`. Repo muss öffentlich sein.

## Hausregeln für die Notebooks
- **So einfach wie möglich.** Keine Hilfsfunktionen, keine Klassen, keine Fehlerbehandlung,
  wenn es nicht nötig ist. Lieber zehn verständliche Zeilen als drei clevere.
- Texte, Kommentare und Instruktionen **auf Deutsch**, kurz. Jeder neue Begriff bekommt eine Erklärung.
- Modell immer über LiteLlm mit den Variablen aus den Secrets:
  `LiteLlm(model="openai/" + MODEL, api_base=BASE_URL, api_key=API_KEY)`.
  `openai/` = OpenAI-kompatibler Anbieter (z.B. OpenRouter). Das Secret `MODEL` enthält nur
  die Modell-ID des Anbieters, ohne `openai/`. Anderes Modell für einen einzelnen Agenten:
  `MODEL` durch einen Text ersetzen. Keine Modellnamen fest in den Code schreiben.
- Keine Gemini-only-Tools wie `google_search` (gehen über LiteLLM nicht).
- Jedes Notebook ist eigenständig: Installation, Key, Code, Frage. Keine Dateien im Repo nötig.
- Agenten laufen in Zellen, kein `adk web`. Ausgabe in drei Zellen getrennt:
  1. `ereignisse = await runner.run_debug("...")` ohne `verbose`: zeigt nur die Texte der Agenten.
     Zuweisen ist wichtig, sonst zeigt Colab die lange Event-Liste als Rückgabewert an.
  2. Schleife über `ereignisse`, druckt nur `function_call` und `function_response`.
  3. `ereignisse` allein: alle Details (Modell, Tokens, `state_delta`).
  State lesen: `runner.session_service.get_session(app_name=runner.app_name,
  user_id="debug_user_id", session_id="debug_session_id")`.
- Nach einer Codeänderung müssen alle Zellen darunter neu ausgeführt werden
  (der Agent hält eine Referenz auf die alte Funktion).
- Klassische Klassen (`LoopAgent` usw.) statt `Workflow`, weil sie zu den Kursfolien passen.
  Die Deprecation-Warnung im Notebook erwähnen.

## Secrets
- Teilnehmende legen in Colab drei Secrets an (Werte von Moodle): `BASE_URL`, `API_KEY`, `MODEL`.
  Das Notebook liest sie mit `userdata.get(...)` in gleichnamige Variablen. Keine Umgebungsvariablen.
- Die lokale `.env` niemals lesen, ausgeben oder ändern.

## Lokal testen (nur für die Pflege)
- `.venv` im Projektordner mit `google-adk` (2.15 getestet) und `litellm`. Unter Windows fehlt die
  Zeitzonen-Datenbank (`pip install tzdata`), Colab hat sie.
- Tests ohne API-Key mit einem Fake-Modell (Unterklasse von `BaseLlm`). Testskripte nicht
  im Projektordner ausführen, damit keine `.env` automatisch geladen wird.
