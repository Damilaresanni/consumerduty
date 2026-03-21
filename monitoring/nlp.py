import spacy
from functools import lru_cache
from spacy.matcher import PhraseMatcher


@lru_cache(maxsize=1)
def get_nlp():
    return spacy.load("en_core_web_sm")


FCA_RULES = [
    {
        "name": "Unclear Fees",
        "fca_ref": "PRIN 12.3.1R",
        "severity": "medium",
        "description": "Potentially unclear or unfair description of fees/charges.",
        "keywords": ["fee", "fees", "charge", "charges", "additional cost"],
    },
    {
        "name": "Guarantee-like Wording",
        "fca_ref": "CONC 3.3.1R",
        "severity": "high",
        "description": "Language that may overstate guarantees or downplay risk.",
        "keywords": ["guaranteed", "no risk", "risk-free"],
    },
    {
        "name": "Complex Jargon",
        "fca_ref": "PRIN 7",
        "severity": "low",
        "description": "Potentially complex jargon that may not be understood by retail customers.",
        "keywords": ["derivative", "structured product"],
    },
]


def build_phrase_matcher():
    nlp = get_nlp()  

    phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    for rule in FCA_RULES:
        nlp.vocab.strings.add(rule["name"])

        patterns = [nlp.make_doc(k) for k in rule["keywords"]]
        phrase_matcher.add(rule["name"], patterns)

    return phrase_matcher


RULE_MAP = {r["name"]: r for r in FCA_RULES}


def run_spacy_rules(text: str):
    nlp = get_nlp()  
    doc = nlp(text)

    phrase_matcher = build_phrase_matcher()

    findings = []
    matches = phrase_matcher(doc)

    for match_id, start, end in matches:
        span = doc[start:end]
        rule_name = nlp.vocab.strings[match_id]

        rule = RULE_MAP[rule_name]

        findings.append({
            "rule_name": rule["name"],
            "fca_ref": rule["fca_ref"],
            "severity": rule["severity"],
            "description": rule["description"],
            "start": span.start_char,
            "end": span.end_char,
            "snippet": span.text,
        })

    return findings