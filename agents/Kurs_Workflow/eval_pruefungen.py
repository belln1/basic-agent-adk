"""Eigene Eval-Prüfung für den Kurs_Workflow.

Eine Eval (Evaluation) ist ein automatischer Test für einen Agenten.
ADK ruft diese Funktion nach jedem Testlauf auf. Sie bekommt alles, was passiert ist,
und gibt eine Punktzahl zwischen 0 und 1 zurück.

Geprüft wird, was die Agenten in den State geschrieben haben (output_key):
- "kurstag" muss den Raum aus dem Stundenplan enthalten
- "wetter" muss eine Temperatur in °C enthalten
"""

from google.adk.evaluation.eval_metrics import EvalStatus
from google.adk.evaluation.evaluator import EvaluationResult, PerInvocationResult

from Kurs_Assistent.agent import naechster_kurstag


def state_pruefen(eval_metric, actual_invocations, expected_invocations, conversation_scenario):
    # Die letzte Textantwort jedes Agenten einsammeln. Genau dieser Text landet
    # über output_key im State.
    antworten = {}
    for ereignis in actual_invocations[0].intermediate_data.invocation_events:
        for teil in ereignis.content.parts if ereignis.content else []:
            if teil.text:
                antworten[ereignis.author] = teil.text

    kurstag = antworten.get("Kurstag_Agent", "")
    wetter = antworten.get("Wetter_Agent", "")
    raum = naechster_kurstag()["kurstag"]["raum"]  # das richtige Ergebnis direkt aus der CSV

    punkte = 0
    if raum in kurstag:
        punkte += 1
    if "°C" in wetter:
        punkte += 1
    score = punkte / 2  # 0, 0.5 oder 1

    print(f"\n[state_pruefen] Raum '{raum}' in kurstag: {raum in kurstag} | °C in wetter: {'°C' in wetter}")
    print(f"  kurstag = {kurstag[:120]!r}")
    print(f"  wetter  = {wetter[:120]!r}")

    status = EvalStatus.PASSED if score == 1 else EvalStatus.FAILED
    # ADK will ein Ergebnis pro Gesprächsrunde und eines fürs Ganze. Hier gibt es nur eine Runde.
    return EvaluationResult(
        overall_score=score,
        overall_eval_status=status,
        per_invocation_results=[
            PerInvocationResult(actual_invocation=actual_invocations[0], score=score, eval_status=status)
        ],
    )
