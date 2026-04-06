import re
import spacy
import textstat
from functools import lru_cache
from spacy.matcher import PhraseMatcher


@lru_cache(maxsize=1)
def get_nlp():
    return spacy.load("en_core_web_sm")



FCA_RULES = [
     
    {
    "name": "Low Readability (Complex Language)",
    "fca_ref": "PRIN 7",
    "severity": "medium",
    "description": "Text may be too complex for retail customers.",
    "type": "readability",

    "thresholds": {
        "flesch_reading_ease": 60,
        "fk_grade": 9,
        "max_sentence_length": 20
    },

    "explanation_template": (
        "The text has a readability score of {score}, which may be too complex "
        "for retail customers."
    ),

    "suggestion": "Use shorter sentences and simpler words."
},
     
    {
        "name": "Guarantee-like Wording",
        "fca_ref": "CONC 3.3.1R",
        "severity": "high",
        "description": "Language that may overstate guarantees or downplay risk",

        
        "keywords": ["guaranteed", "no risk", "risk-free"],

        
        "regex_patterns": [r"\bguaranteed\b", r"\bno risk\b", r"\brisk[- ]?free\b"],

        "negation_patterns": [r"not guaranteed", r"not risk[- ]?free"],

        "explanation_template": "The phrase '{match}' may mislead customers into believing there is no risk.",
        "suggestion": "Use balanced language and include risk disclaimers."
    },
     
    {
        "name": "Absolute Guarantee Claims",
        "fca_ref": "CONC 3.3.1R",
        "severity": 5,
        "description": "Language used may overstate guarantees",
        "category": "Misleading Claims",
        "keywords": ["guaranteed", "assured returns", "certain returns"],
        "regex_patterns": [r"\bguaranteed\b", r"\bassured returns?\b", r"\bcertain returns?\b"],
        "spacy_patterns": [[{"LOWER": "guaranteed"}], [{"LOWER": "assured"}, {"LOWER": "returns"}]],
        "negation_patterns": [r"not guaranteed", r"no guarantee"],
        "explanation_template": "The term '{match}' implies certainty of returns, which may mislead customers.",
        "suggestion": "Use 'target returns' and clearly state risks."
    },
    
    {
        "name": "Risk-Free Language",
        "fca_ref": "CONC 3.3.1R",
        "severity": 5,
        "description": "Language that may overstate guarantees or downplay risk",
        "category": "Misleading Claims",
        "keywords": ["zero risk", "no risk", "risk-free"],
        "regex_patterns": [r"\brisk[- ]?free\b", r"\bno risk\b", r"\bzero risk\b"],
        "spacy_patterns": [[{"LOWER": "risk"}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": "free"}]],
        "negation_patterns": [r"not risk[- ]?free"],
        "explanation_template": "The phrase '{match}' suggests there is no risk, which is misleading for financial products.",
        "suggestion": "Use 'low risk' and explain the actual risks involved."
    },
   {
        "name": "Unrealistic Return Promises",
        "fca_ref": "COBS 4.2",
        "severity": 5,
        "description": "This sentence may mislead customers with false claims",
        "category": "Misleading Claims",
        "keywords": ["earn", "double your money", "high returns", "fast profits"],
        "regex_patterns": [r"\bearn \£?\d{3,}", r"\bdouble your money\b", r"\bhigh returns\b", r"\bfast profits?\b"],
        "spacy_patterns": [[{"LOWER": "earn"}, {"LIKE_NUM": True}], [{"LOWER": "high"}, {"LOWER": "returns"}]],
        "negation_patterns": [],
        "explanation_template": "The phrase '{match}' may create unrealistic expectations about returns.",
        "suggestion": "Provide balanced information including risks and variability of returns."
    },
    {
        "name": "Vague Fee Disclosure",
        "fca_ref": "PRIN 2.1.1.7",
        "severity": 4,
        "description": "Fee disclosure might not be clear enough",
        "category": "Cost Transparency",
        "keywords": ["fees may apply", "additional costs", "charges could", "minimal fees"],
        "regex_patterns": [r"fees may apply", r"additional costs?", r"charges could", r"minimal fees"],
        "spacy_patterns": [[{"LOWER": "fees"}, {"LOWER": "may"}, {"LOWER": "apply"}]],
        "negation_patterns": [],
        "explanation_template": "The phrase '{match}' is vague and does not clearly explain actual costs.",
        "suggestion": "State specific fees (e.g., '£10 monthly fee')."
    },
    
      {
        "name": "Downplayed Risk",
        "fca_ref": "COBS 4.5",
        "severity": 4,
        "description": "Language may downplay risk",
        "category": "Risk Disclosure",
        "keywords": ["low risk", "safe investment", "secured returns"],
        "regex_patterns": [r"\blow risk\b", r"\bsafe investment\b", r"\bsecure returns?\b"],
        "spacy_patterns": [[{"LOWER": "low"}, {"LOWER": "risk"}], [{"LOWER": "safe"}, {"LOWER": "investment"}]],
        "negation_patterns": [],
        "explanation_template": "The phrase '{match}' may understate the level of risk involved.",
        "suggestion": "Clearly describe risks alongside potential benefits."
    },
   {
        "name": "Complex Financial Jargon",
        "fca_ref": "2.1.1.7",
        "severity": 2,
        "description": "Possibility of complex financial terms exsits",
        "category": "Clarity",
        "keywords": ["derivatives", "structured products", "hedging", "volatility"],
        "regex_patterns": [r"\bderivatives?\b", r"\bstructured products?\b", r"\bhedging\b", r"\bvolatility\b"],
        "spacy_patterns": [[{"LOWER": "derivatives"}], [{"LOWER": "structured"}, {"LOWER": "products"}]],
        "negation_patterns": [],
        "explanation_template": "The term '{match}' may not be understood by retail customers.",
        "suggestion": "Use simpler language or provide a clear explanation."
    },
    {
        "name": "Missing Risk Disclaimer",
        "fca_ref": "CONC 3.5",
        "severity": 5,
        "description": "Risk disclaimer might not be clear",
        "category": "Risk Disclosure",
        "keywords": ["earn", "invest", "returns"],
        "regex_patterns": [r"\bearn\b", r"\binvest\b", r"\breturns?\b"],
        "spacy_patterns": [[{"LOWER": "earn"}], [{"LOWER": "invest"}]],
        "negation_patterns": [],
        "explanation_template": "The content promotes financial benefits without any visible risk warning.",
        "suggestion": "Include a clear and prominent risk disclaimer."
    },
     {
        "name": "Pressure Selling Language",
        "fca_ref": "Consumer Duty",
        "severity": 4,
        "description": "Customers might be pressured to act based on the language",
        "category": "Fairness",
        "keywords": ["limited time", "act now", "don't miss out","only today"],
        "regex_patterns": [r"\blimited time\b", r"\bact now\b", r"\bdon't miss out\b", r"\bonly today\b"],
        "spacy_patterns": [[{"LOWER": "limited"}, {"LOWER": "time"}], [{"LOWER": "act"}, {"LOWER": "now"}]],
        "negation_patterns": [],
        "explanation_template": "The phrase '{match}' may pressure customers into making quick decisions.",
        "suggestion": "Avoid urgency that prevents informed decision-making."
    },
      {
        "name": "One-Sided Promotion",
        "fca_ref": "PRIN 7",
        "severity": 4,
        "description": "The details of the product is overhyped",
        "category": "Fairness",
        "keywords": ["high", "high returns", "strong performance"],
        "regex_patterns": [r"\bhigh returns\b", r"\bstrong performance\b"],
        "spacy_patterns": [[{"LOWER": "high"}, {"LOWER": "returns"}]],
        "negation_patterns": [],
        "explanation_template": "The content highlights benefits without mentioning risks.",
        "suggestion": "Include balanced information about risks and limitations."
    },
     {
        "name": "Ambiguous Performance Claims",
        "fca_ref": "COBS 4.5",
        "severity": 3,
        "description": "Language that may not be clear and overstate performance of the product",
        "category": "Misleading Claims",
        "keywords": ["best performing", "top returns", "outperform"],
        "regex_patterns": [r"\bbest performing\b", r"\btop returns\b", r"\boutperform\b"],
        "spacy_patterns": [[{"LOWER": "best"}, {"LOWER": "performing"}]],
        "negation_patterns": [],
        "explanation_template": "The phrase '{match}' lacks context or supporting data.",
        "suggestion": "Provide evidence, timeframes, and benchmarks."
    }
   
   
   
   
   
   
   
   
   
   
   
   
   
   
]



def check_readability(text, rule):
    scores = {
        "flesch": textstat.flesch_reading_ease(text),
        "fk_grade": textstat.flesch_kincaid_grade(text),
        "sentence_length": textstat.avg_sentence_length(text)
    }

    thresholds = rule["thresholds"]

    issues = []

    if scores["flesch"] < thresholds["flesch_reading_ease"]:
        issues.append("low_flesch")

    if scores["fk_grade"] > thresholds["fk_grade"]:
        issues.append("high_grade")

    if scores["sentence_length"] > thresholds["max_sentence_length"]:
        issues.append("long_sentences")

    return issues, scores



def match_regex(text, rule):
    matches = []

    for pattern in rule.get("regex_patterns", []):
        for m in re.finditer(pattern, text, re.IGNORECASE):
            matches.append(m)

    return matches

def is_negated(text, start, end, negation_patterns):
    window = text[max(0, start-20):end+20]

    for neg in negation_patterns:
        if re.search(neg, window, re.IGNORECASE):
            return True

    return False

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
            "snippet": span.text
           
        })
        
        
        
        
    for rule in FCA_RULES:
        if rule.get("type") == "readability":
            issues, scores = check_readability(text, rule)
            
            if issues:
                findings.append({
                    "rule_name": rule["name"],
                    "fca_ref": rule["fca_ref"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "snippet": text[:200],

                    "metrics": scores,

                    "explanation": rule["explanation_template"].format(
                        score=round(scores["flesch"], 1)
                    ),

                    "suggestion": rule["suggestion"]
                })
                
                
        regex_matches = match_regex(text, rule)

        for m in regex_matches:
            # Negation check
            if is_negated(
                text,
                m.start(),
                m.end(),
                rule.get("negation_patterns", [])
            ):
                continue

            findings.append({
                "rule_name": rule["name"],
                "fca_ref": rule["fca_ref"],
                "severity": rule["severity"],
                "description": rule["description"],
                "start": m.start(),
                "end": m.end(),
                "snippet": m.group(),

                # NEW FIELDS
                "explanation": rule.get("explanation_template", "").replace("{match}", m.group()),
                "suggestion": rule.get("suggestion", "")
            })


    return findings





