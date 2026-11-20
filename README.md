# Agenten bauen mit Google ADK

Zwei Beispiel-Agenten zum Ausprobieren in Google Colab. Du brauchst nur einen Browser und
ein Google-Konto, installieren musst du nichts.

| Notebook | Was du lernst | Öffnen |
|---|---|---|
| **Zeitansage_Agent** | Ein Agent mit einem Tool. Wann ruft er das Tool auf, und was passiert mit dem Ergebnis? | [![In Colab öffnen](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/belln1/basic-agent-adk/blob/main/Zeitansage_Agent.ipynb) |
| **Finanzberater_Agent** | Zwei Agenten in einer Schleife: ein Berater schreibt, eine Compliance-Prüfung kontrolliert. Harte Regeln in Python, weiche Regeln per Sprachmodell. | [![In Colab öffnen](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/belln1/basic-agent-adk/blob/main/Finanzberater_Agent.ipynb) |

Am besten zuerst den Zeitansage_Agent.

## So geht's

1. Oben auf **In Colab öffnen** klicken.
2. **Datei → Kopie in Drive speichern.** Sonst gehen deine Änderungen verloren.
3. Links auf das **Schlüssel-Symbol** (Secrets) klicken und ein Secret anlegen:
   Name `API_KEY`, Wert = der Key von Moodle. **Notebook-Zugriff** einschalten.
4. Die Zellen von oben nach unten ausführen (Play-Knopf links an jeder Zelle).

Wenn du nach einer Pause weitermachst, hat Colab alles vergessen. Dann einfach wieder
oben beginnen. Das Secret bleibt gespeichert.
