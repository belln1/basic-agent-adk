# CAS-Agentenprojekt (Google ADK mit Gemini, in Google Colab)

Lernprojekt eines Weiterbildungskurses (CAS, ZHAW). Die Teilnehmenden sind keine
Software-Entwickler. Ziel ist, Konzepte zu verstehen, nicht produktiven Code zu schreiben.
Sie arbeiten nur in Google Colab, mit Gemini als Code-Assistent (nicht Claude Code).
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
- Modell: `model="gemini-3.5-flash"` (direkt als Text, ohne LiteLlm).
- Jedes Notebook ist eigenständig: Installation, Key, Code, Frage. Keine Dateien im Repo nötig.
- Agenten laufen in Zellen: `runner = InMemoryRunner(agent=root_agent)` und
  `await runner.run_debug("...", verbose=True)` (zeigt Tool-Aufrufe). Kein `adk web`.
  State lesen: `runner.session_service.get_session(app_name=runner.app_name,
  user_id="debug_user_id", session_id="debug_session_id")`.
- Nach einer Codeänderung müssen alle Zellen darunter neu ausgeführt werden
  (der Agent hält eine Referenz auf die alte Funktion).
- Klassische Klassen (`LoopAgent` usw.) statt `Workflow`, weil sie zu den Kursfolien passen.
  Die Deprecation-Warnung im Notebook erwähnen.

## API-Key
- Teilnehmende legen in Colab ein Secret `API_KEY` an (Key von Moodle). Das Notebook setzt
  `os.environ["GOOGLE_API_KEY"] = userdata.get("API_KEY")`.
- Die lokale `.env` niemals lesen, ausgeben oder ändern.

## Lokal testen (nur für die Pflege)
- `.venv` im Projektordner mit `google-adk` (2.15 getestet). Unter Windows fehlt die
  Zeitzonen-Datenbank (`pip install tzdata`), Colab hat sie.
- Tests ohne API-Key mit einem Fake-Modell (Unterklasse von `BaseLlm`). Testskripte nicht
  im Projektordner ausführen, damit keine `.env` automatisch geladen wird.
