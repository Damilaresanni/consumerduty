import spacy
from spacy.matcher import Matcher, PhraseMatcher

nlp = spacy.load("en_core_web_sm")

# -----------------------------
# FCA RULE DEFINITIONS
# -----------------------------

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



matcher = Matcher(nlp.vocab)
phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for rule in FCA_RULES:
    patterns = [nlp.make_doc(k) for k in rule["keywords"]]
    phrase_matcher.add(rule["name"], patterns)
    
    
def run_spacy_rules(text: str):
    doc = nlp(text)
    findings = []
    
    for rule in FCA_RULES:
        matches = phrase_matcher(doc, as_spans=True)
        for span in matches:
            findings.append({
                "rule_name": rule["name"],
                "fca_ref": rule["fca_ref"],
                "severity": rule["severity"],
                "description": rule["description"],
                "start":span.start_char,
                "end":span.end_char,
                "snippet":span.text,
            })
            
    return findings



