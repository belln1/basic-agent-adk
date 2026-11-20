# Setup-Anleitung für Claude

Du richtest dieses Kursprojekt (Google ADK mit Claude) auf einem Windows-Laptop ein.
Die Person ist keine Entwicklerin und hat keine Admin-Rechte. Arbeite die Schritte der
Reihe nach ab und sag nach jedem Schritt in einem Satz, was passiert ist.

## Regeln
- Nichts mit Admin-Rechten, nichts systemweit installieren.
- Python, Cache und Umgebung von uv liegen unter `%USERPROFILE%\.uv`, **nicht** in AppData
  und nicht im Projektordner. Die Claude-App leitet Schreibzugriffe auf AppData um, dann
  bricht die Python-Installation ab.
- Die Datei `.env` niemals lesen, ausgeben oder ändern. Erlaubt ist nur zu prüfen, ob sie
  existiert, und sie zu verschieben oder umzubenennen (Schritt 5). Den Key nie in den Chat holen.
- Die Datei `daten/empfaenger.csv` nie im Chat ausgeben.
- Den Server (`start_adk.cmd`) startet die Person selbst.

## Schritt 1: uv prüfen oder installieren
Prüfe, ob `%USERPROFILE%\.local\bin\uv.exe` existiert. Falls nicht, installiere uv
(kein Admin nötig, landet in `%USERPROFILE%\.local\bin`):

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Wenn das blockiert wird (Firewall, Richtlinie): abbrechen und der Person sagen, sie soll
die Kursleitung fragen.

## Schritt 2: Python und Pakete installieren
Im Projektordner, in PowerShell, mit denselben Variablen wie in `start_adk.cmd`:

```
$env:UV_PYTHON_INSTALL_DIR = "$env:USERPROFILE\.uv\python"
$env:UV_CACHE_DIR = "$env:USERPROFILE\.uv\cache"
$env:UV_PROJECT_ENVIRONMENT = "$env:USERPROFILE\.uv\envs\CAS_MyAgents"
$env:UV_PYTHON_PREFERENCE = "only-managed"
& "$env:USERPROFILE\.local\bin\uv.exe" sync --group eval
```

Das lädt Python 3.12 und alle Pakete, auch die für die Evals (rund 350 MB, 2 bis 5 Minuten).
Lass den Befehl im Hintergrund laufen und sag der Person, dass es dauert.

## Schritt 3: Testen
Mit denselben Variablen:

```
& "$env:USERPROFILE\.local\bin\uv.exe" run python -c "import google.adk, litellm, mcp; print('Setup OK')"
```

## Schritt 4: Eigene E-Mail-Adresse
Frag die Person nach ihrer E-Mail-Adresse und ersetze in `daten/empfaenger.csv` in der
Zeile `master` die Platzhalter-Adresse. Die anderen Zeilen nicht ändern.

## Schritt 5: API-Key (Datei .env von Moodle)
Die Datei `.env` mit dem Kurs-Key ist **nicht** im ZIP. Sie liegt separat auf Moodle.
Ihren Inhalt nie öffnen, lesen oder ausgeben, auch nicht zur Kontrolle.

1. Prüfe nur, ob im Projektordner eine Datei `.env` existiert: `Test-Path .env`
2. Falls ja: weiter mit Schritt 6.
3. Falls nein, sag der Person: «Lade auf Moodle die Datei .env herunter und speichere sie
   in diesen Projektordner: <vollständiger Pfad des Projektordners>. Sag mir, wenn sie dort ist.»
   Warte, bis sie bestätigt.
4. Browser speichern die Datei manchmal unter einem anderen Namen (`env`, `env.txt`,
   `.env.txt`) oder im Ordner Downloads. Prüfe mit `Test-Path`, ob eine dieser Dateien im
   Projektordner oder in `$env:USERPROFILE\Downloads` liegt. Frag die Person, bevor du eine
   Datei verschiebst, und benenne sie dann mit `Move-Item` in `.env` im Projektordner um.
5. Prüfe am Schluss noch einmal mit `Test-Path .env`.

## Schritt 6: Abschluss
Sag der Person genau das:
1. Im Explorer im Projektordner auf **start_adk.cmd** doppelklicken. Das schwarze Fenster
   offen lassen, es ist der Server. Beenden mit Strg+C.
2. Im Browser **http://127.0.0.1:8000** öffnen.
3. Oben links **Zeitansage_Agent** wählen und fragen: «Wie spät ist es?»
4. Nach jeder Änderung am Code: im schwarzen Fenster Strg+C, dann wieder start_adk.cmd.
