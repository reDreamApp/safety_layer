from AI.prompts import SYSTEM_PROMPT_TEMPLATES_DE, SYSTEM_PROMPT_TEMPLATES_EN


def test_summary_prompts_require_grounded_non_cinematic_details():
    english = SYSTEM_PROMPT_TEMPLATES_EN["summary"]
    german = SYSTEM_PROMPT_TEMPLATES_DE["summary"]

    assert "Do not write in a literary, dramatic, or cinematic style" in english
    assert "Every concrete detail must be directly traceable" in english
    assert "Do not infer emotions or body sensations unless the user stated them" in english
    assert "Preserve the user's sequence of locations and events" in english
    assert "Do not make the scene more vivid, warm, hopeful, dramatic, or complete" in english
    assert "write generally instead of inventing it" in english
    assert "Summarize the rewritten dream faithfully in 3-5 sentences" in english
    assert "Do not expand sparse details into a richer scene" in english
    assert "Schreibe nicht literarisch, dramatisch oder filmisch" in german
    assert "Jede konkrete Information muss direkt auf eine Aussage des Nutzers zurückführbar sein" in german
    assert "Ziehe keine emotionalen oder körperlichen Schlüsse" in german
    assert "Bewahre die Reihenfolge der Orte und Ereignisse" in german
    assert "Mache die Szene nicht lebendiger, wärmer, hoffnungsvoller" in german
    assert "schreibe allgemein statt es zu erfinden" in german
    assert "Fasse den umgeschriebenen Traum in 3-5 Sätzen getreu zusammen" in german
    assert "Erweitere knappe Angaben nicht zu einer reicheren Szene" in german


def test_summary_prompts_require_final_confirmation_line():
    english = SYSTEM_PROMPT_TEMPLATES_EN["summary"]
    german = SYSTEM_PROMPT_TEMPLATES_DE["summary"]

    assert "The final line of your response MUST be exactly: Are you satisfied with the generated summary?" in english
    assert "Die letzte Zeile deiner Antwort MUSS exakt lauten: Bist du mit der generierten Zusammenfassung zufrieden?" in german
