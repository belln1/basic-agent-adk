# CAS-Agentenprojekt (Google ADK mit Claude)

Lernprojekt eines Weiterbildungskurses (CAS, ZHAW). Die Teilnehmenden sind keine
Software-Entwickler. Ziel ist, Konzepte zu verstehen, nicht produktiven Code zu schreiben.

## Hausregeln für den Code
- **So einfach wie möglich.** Keine Hilfsfunktionen, keine Klassen, keine Fehlerbehandlung,
  wenn es nicht nötig ist. Lieber zehn verständliche Zeilen als drei clevere.
- Kommentare und Instruktionen **auf Deutsch**, kurz. Jeder neue Begriff bekommt einen Kommentar.
- **Modelle immer über LiteLlm, nie Gemini** (die ADK-Beispiele und der Skill nutzen Gemini):
  - `LiteLlm(model="anthropic/claude-haiku-5-5")` für einfache Schritte (Standard)
  - `LiteLlm(model="anthropic/claude-sonnet-5-5")` nur zum Interpretieren oder Schreiben
- Keine Gemini-only-Tools wie `google_search` oder `url_context`. Webseiten mit `httpx`
  in einem Python-Tool laden.
- Agentennamen sind Python-Bezeichner (`Kurs_Assistent`), Ordnername = `name` des Root-Agenten.

## Projektaufbau
- `agents/<Name>/agent.py` definiert `root_agent`, `agents/<Name>/__init__.py` enthält `from . import agent`.
- `.env` liegt im **Projektordner** (nicht im Agentenordner) mit `ANTHROPIC_API_KEY`.
  Die Teilnehmenden laden sie separat von Moodle. Die `.env` niemals lesen, ausgeben oder ändern.
- `daten/` enthält Stundenplan und Empfängerliste. Die Empfängerliste nie ausgeben.
- Gestartet wird mit `start_adk.cmd` (setzt die uv-Pfade, startet `adk web agents --port 8000`).
  Die Person startet den Server selbst. Nach jeder Codeänderung muss sie ihn neu starten
  (Strg+C, dann erneut `start_adk.cmd`), weil `--reload` unter Windows nicht geht.
- Pakete nur mit uv hinzufügen. Vorher in der Shell die Variablen aus `start_adk.cmd` setzen.

## Bestehende Agenten als Vorlage
- `Zeitansage_Agent`: ein Agent mit einem Tool, `tool_context`, `skip_summarization`-Demo.
- `Kurs_Assistent`: ein Agent, der selbst entscheidet. Vier Tools, `before_model_callback`
  (Themen-Guardrail), `before_tool_callback` (Empfängerliste), E-Mail als Outlook-Entwurf.
- `Kurs_Workflow`: dieselbe Aufgabe als fester Ablauf mit `SequentialAgent`, `ParallelAgent`,
  `output_key` und `{platzhalter}` aus dem State. Importiert die Tools von `Kurs_Assistent`.
- `Finanzberater_Agent`: `LoopAgent` (max. 3 Runden) aus Berater (Haiku) und Compliance-Prüfer
  (Sonnet, Tool `exit_loop`). Ein `after_agent_callback` prüft harte Regeln in Python und legt
  das Ergebnis als `regelcheck` in den State. `{kritik?}` = optionaler Platzhalter für Runde 1.
- `Kurs_MCP`: Agent ohne eigene Tools. Holt sie per `McpToolset` + `StdioConnectionParams`
  vom eigenen Server `mcp_server/kurs_server.py` (Tools `naechster_kurstag`, `stundenplan`).
  Der Agent startet den Server selbst mit `sys.executable`. Getestet in `adk web` unter Windows.

## MCP
- Paket `mcp` ist Version 2.x: `FastMCP` heisst jetzt `MCPServer`
  (`from mcp.server.mcpserver import MCPServer`, `@server.tool()`, `server.run()`).
- MCP-Server liegen in `mcp_server/`, nicht unter `agents/` (dort wäre jeder Ordner ein Agent).
- Im stdio-Server nie `print()` verwenden, stdout ist die Leitung zum Client.
- Externe MCP-Server über `npx` brauchen Node.js, das ist auf den Kurs-Laptops nicht vorausgesetzt.

## Evals (automatische Tests)
- Beispiel in `agents/Kurs_Workflow/`: `kurs_workflow.evalset.json` (Testfälle),
  `test_config.json` (Metriken), `eval_pruefungen.py` (eigene Metrik `state_pruefen`).
  Gestartet mit `start_eval.cmd`. Ergebnisse landen in `agents/<Name>/.adk/eval_history/`.
- `adk eval` setzt den Ordner `agents` NICHT auf den Python-Pfad: `PYTHONPATH=agents` setzen.
- Nicht `google-adk[eval]` installieren (zwingt eine alte litellm-Version). Stattdessen
  liegen `pandas`, `tabulate`, `rouge-score` und `google-cloud-aiplatform` in der uv-Gruppe
  `eval` (ca. 115 MB). `start_eval.cmd` nutzt `uv run --group eval`, lädt sie also beim
  ersten Mal selbst. Das normale Setup (`start_adk.cmd`) braucht sie nicht.
- Ohne Gemini nutzbar: `tool_trajectory_avg_score` (mit `match_type` ANY_ORDER bei Parallel)
  und eigene Python-Metriken. LLM-als-Richter-Metriken nutzen standardmässig Gemini.
- Eigene Metrik: Funktion `(eval_metric, actual_invocations, expected_invocations,
  conversation_scenario)` gibt `EvaluationResult` mit `per_invocation_results` zurück.
- `include_contents="none"` blendet nur den früheren Verlauf aus. Der erste Agent sieht die
  aktuelle Frage trotzdem, schützt also nicht vor Ablenkung wie "erzähl einen Katzenwitz".

## Workflow oder klassische Klassen
`SequentialAgent`, `ParallelAgent` und `LoopAgent` sind in ADK 2.x veraltet (Warnung im
Terminal), funktionieren aber. Der Nachfolger ist `Workflow` (siehe Skill `adk-agent-builder`).
- Standard im Kurs: die **klassischen Klassen**, weil sie zu den Kursfolien passen.
- `Workflow` nur, wenn die Person es ausdrücklich will. Getestet mit Claude und der
  SQLite-Session von `adk web` (nicht in der Weboberfläche selbst): `("START", a, (b, c))`, `((b, c), JoinNode(name="sammeln"))`, `(join, d)`
  funktioniert, `output_key` und `{platzhalter}` gehen wie gewohnt.
  Stolperstein: Ein Agent-Objekt darf nicht gleichzeitig in einem `SequentialAgent` und in
  einem `Workflow` stecken (Fehler "mode='chat'"). Für jede Variante eigene Agent-Objekte anlegen.

## Chef-Agent: Beauftragen oder Weitergeben
Das Feld `sub_agents` hat zwei Bedeutungen. Bei `SequentialAgent`, `ParallelAgent` und `LoopAgent`
sind es feste Schritte (Code entscheidet). Bei einem normalen `Agent` sind es Kollegen, an die
das LLM delegiert. Dafür gibt es zwei Arten:
- **Beauftragen (Standard):** Der Chef ruft den Unteragenten wie ein Tool auf und bekommt das
  Resultat zurück. Er bleibt verantwortlich, kann prüfen, zusammenfassen, weitermachen.
  Umsetzung: Unteragent mit `mode="single_turn"` und klarer `description` in `sub_agents` des
  Chefs (der Unteragent antwortet einfach mit Text). Nimm das immer, wenn der Chef «zerlegt»,
  «überwacht», «prüft» oder «zusammenführt».
  Der Chef vergibt die Aufträge nacheinander, nicht parallel. Für echte Parallelität einen
  `ParallelAgent` verwenden.
  Gleiches Verhalten, klassisch: `tools=[AgentTool(agent=unteragent)]`
  (`from google.adk.tools import AgentTool`). Nimm das, falls `mode` Probleme macht.
- **Weitergeben:** `sub_agents` ohne `mode`. Das LLM übergibt das Gespräch mit
  `transfer_to_agent`. Danach beantwortet der Unteragent auch die **folgenden** Fragen, der
  Chef ist draussen. Nur für Empfang oder Triage, wo der Fachagent übernehmen soll.
- Getestet mit ADK 2.14 und einem Test-Modell (ohne echte API-Aufrufe): Beim Beauftragen geht
  die nächste Frage wieder an den Chef, beim Weitergeben an den Unteragenten.

## Wenn jemand ein Bild (Flipchart, Skizze) eines Agenten-Ablaufs schickt
1. **Zuerst beschreiben, was du im Bild erkennst**, als kurze Liste: welche Agenten, welche
   Tools, welche Pfeile. Lies Pfeile so:
   - Kette A → B → C: `SequentialAgent`
   - Verzweigung, die wieder zusammenläuft: `ParallelAgent` innerhalb eines `SequentialAgent`
   - Pfeil zurück (Schleife): `LoopAgent` mit `max_iterations` und dem Tool `exit_loop`
   - ein Chef-Agent, der verteilt: siehe Abschnitt «Chef-Agent: Beauftragen oder Weitergeben».
     Im Zweifel **Beauftragen**, und in der Beschreibung des Bilds sagen, welche Variante du nimmst.
   - Schloss, Ampel, Stopp-Schild: Callback als Guardrail
2. **Dann höchstens drei Rückfragen** stellen, nur zu dem, was im Bild fehlt oder unklar ist,
   z.B. was ein Tool tun soll, welche Daten es gibt, Haiku oder Sonnet.
3. Erst nach der Antwort bauen: einen neuen Ordner unter `agents/`, eine `agent.py`.
   Tools, die es nur als Idee gibt, als einfache Python-Funktion mit Beispieldaten umsetzen.
4. Zum Schluss sagen: Server neu starten, Agent oben links auswählen, eine Testfrage vorschlagen.
