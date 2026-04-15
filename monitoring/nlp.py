import re
import spacy
import textstat
from functools import lru_cache
from spacy.matcher import PhraseMatcher



@lru_cache(maxsize=1)
def get_nlp():
    return spacy.load("en_core_web_sm")


FCA_RULES = [

    # ──────────────────────────────────────────────────────────────────────
    # CATEGORY: Misleading Claims
    # ──────────────────────────────────────────────────────────────────────

    {
        "name": "Guaranteed returns language",
        "fca_ref": "CONC 3.3.1R",
        "severity": 5,
        "category": "Misleading Claims",
        "description": "Language that implies certainty of investment returns.",
        "keywords": ["guaranteed", "assured returns", "certain returns"],
        "regex_patterns": [
            r"\bguaranteed\b",
            r"\bassured returns?\b",
            r"\bcertain returns?\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "guaranteed"}],
            [{"LOWER": "assured"}, {"LOWER": "returns"}],
            [{"LOWER": "certain"}, {"LOWER": "returns"}],
        ],
        "negation_patterns": [r"not guaranteed", r"no guarantee"],
        "explanation_template": (
            "The term '{match}' implies certainty of returns, which may mislead "
            "customers under FCA CONC 3.3.1R."
        ),
        "suggestion": (
            "Replace with 'target returns' and clearly state that investment "
            "returns are not guaranteed and capital is at risk."
        ),
    },

    {
        "name": "Risk-free language",
        "fca_ref": "CONC 3.3.1R",
        "severity": 5,
        "category": "Misleading Claims",
        "description": "Language that implies no risk exists for the investment.",
        "keywords": ["zero risk", "no risk", "risk-free"],
        "regex_patterns": [
            r"\brisk[- ]?free\b",
            r"\bno risk\b",
            r"\bzero risk\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "risk"}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": "free"}],
            [{"LOWER": "no"}, {"LOWER": "risk"}],
            [{"LOWER": "zero"}, {"LOWER": "risk"}],
        ],
        "negation_patterns": [r"not risk[- ]?free"],
        "explanation_template": (
            "The phrase '{match}' suggests there is no risk, which is misleading "
            "for financial products under FCA CONC 3.3.1R."
        ),
        "suggestion": (
            "Remove risk-free language entirely and describe the actual level "
            "of risk involved in the product."
        ),
    },

    {
        "name": "Unrealistic return promises",
        "fca_ref": "COBS 4.2.1R",
        "severity": 5,
        "category": "Misleading Claims",
        "description": "Language that may mislead customers with exaggerated return claims.",
        "keywords": ["double your money", "high returns", "fast profits"],
        "regex_patterns": [
            r"\bearn \£?\d{3,}",
            r"\bdouble your money\b",
            r"\bhigh returns\b",
            r"\bfast profits?\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "earn"}, {"LIKE_NUM": True}],
            [{"LOWER": "high"}, {"LOWER": "returns"}],
            [{"LOWER": "double"}, {"LOWER": "your"}, {"LOWER": "money"}],
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The phrase '{match}' may create unrealistic expectations about "
            "investment returns under FCA COBS 4.2.1R."
        ),
        "suggestion": (
            "Provide balanced information including risks and the variability "
            "of returns. Avoid specific return figures without supporting evidence."
        ),
    },

    {
        "name": "Ambiguous performance claims",
        "fca_ref": "COBS 4.5.2R",
        "severity": 3,
        "category": "Misleading Claims",
        "description": "Superlative or comparative performance language lacking supporting evidence.",
        "keywords": ["best performing", "top returns", "outperform"],
        "regex_patterns": [
            r"\bbest performing\b",
            r"\btop returns\b",
            r"\boutperform\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "best"}, {"LOWER": "performing"}],
            [{"LOWER": "top"}, {"LOWER": "returns"}],
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The phrase '{match}' makes a performance claim that lacks context, "
            "supporting data, or a defined timeframe under FCA COBS 4.5.2R."
        ),
        "suggestion": (
            "Provide evidence, defined timeframes, and relevant benchmarks "
            "for any comparative or superlative performance claim."
        ),
    },

    {
        "name": "Unsubstantiated superlative claims",
        "fca_ref": "COBS 4.2.1R",
        "severity": 3,
        "category": "Misleading Claims",
        "description": "Superlative marketing claims made without supporting evidence.",
        "keywords": ["number one", "best in class", "market leading", "award winning"],
        "regex_patterns": [
            r"\bnumber[- ]?one\b",
            r"\bbest[- ]in[- ]class\b",
            r"\bmarket[- ]leading\b",
            r"\baward[- ]winning\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "number"}, {"LOWER": "one"}],
            [{"LOWER": "market"}, {"LOWER": "leading"}],
            [{"LOWER": "award"}, {"LOWER": "winning"}],
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The claim '{match}' is a superlative without supporting evidence, "
            "which may mislead customers under FCA COBS 4.2.1R."
        ),
        "suggestion": (
            "Provide evidence, source, and date for any superlative or "
            "comparative claim."
        ),
    },

    {
        "name": "Tax benefit misrepresentation",
        "fca_ref": "COBS 4.2.1R",
        "severity": 4,
        "category": "Misleading Claims",
        "description": "Tax benefit claims made without required caveats.",
        "keywords": ["tax free", "no tax", "tax exempt"],
        "regex_patterns": [
            r"\btax[- ]?free\b",
            r"\bno tax\b",
            r"\btax[- ]?exempt\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "tax"}, {"LOWER": "free"}],
            [{"LOWER": "tax"}, {"LOWER": "exempt"}],
        ],
        "requires_absence_of": [
            r"tax treatment depends",
            r"tax laws may change",
            r"individual circumstances",
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The phrase '{match}' implies unconditional tax benefits without "
            "the required caveats under FCA COBS 4.2.1R."
        ),
        "suggestion": (
            "Add: 'Tax treatment depends on individual circumstances and tax "
            "laws may change in the future.'"
        ),
    },

    # ──────────────────────────────────────────────────────────────────────
    # CATEGORY: Risk Disclosure
    # ──────────────────────────────────────────────────────────────────────

    {
        "name": "Downplayed risk",
        "fca_ref": "COBS 4.5.2R",
        "severity": 4,
        "category": "Risk Disclosure",
        "description": "Language that understates the level of investment risk.",
        "keywords": ["low risk", "safe investment", "secured returns"],
        "regex_patterns": [
            r"\blow risk\b",
            r"\bsafe investment\b",
            r"\bsecure returns?\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "low"}, {"LOWER": "risk"}],
            [{"LOWER": "safe"}, {"LOWER": "investment"}],
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The phrase '{match}' may understate the level of risk involved "
            "in the product under FCA COBS 4.5.2R."
        ),
        "suggestion": (
            "Clearly describe the actual risks alongside potential benefits. "
            "Avoid minimising language."
        ),
    },

    {
        "name": "Missing risk disclaimer",
        "fca_ref": "CONC 3.5.1R",
        "severity": 5,
        "category": "Risk Disclosure",
        "description": "Promotional content present without an accompanying risk disclaimer.",
        "keywords": ["invest", "returns", "growth", "profit"],
        "regex_patterns": [
            r"\binvest(ment)?\b",
            r"\breturns?\b",
            r"\bgrowth\b",
            r"\bprofit\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "invest"}],
            [{"LOWER": "returns"}],
        ],
        "requires_absence_of": [
            r"capital (is |at )?risk",
            r"you may (lose|get back less)",
            r"your (capital|money) is at risk",
            r"value of (your )?investment(s)? (can|may) (fall|go down)",
        ],
        "negation_patterns": [],
        "explanation_template": (
            "Promotional language was detected without any visible risk disclaimer "
            "under FCA CONC 3.5.1R."
        ),
        "suggestion": (
            "Include a clear and prominent risk disclaimer such as: "
            "'Your capital is at risk. The value of your investment may fall "
            "as well as rise and you may get back less than you invest.'"
        ),
    },

    {
        "name": "Capital at risk warning missing",
        "fca_ref": "COBS 4.2.1R",
        "severity": 5,
        "category": "Risk Disclosure",
        "description": "Investment promotion detected without a capital-at-risk warning.",
        "keywords": ["invest", "investment", "fund", "portfolio"],
        "regex_patterns": [
            r"\binvest(ment)?\b",
            r"\bfund\b",
            r"\bportfolio\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "investment"}],
            [{"LOWER": "fund"}],
            [{"LOWER": "portfolio"}],
        ],
        "requires_absence_of": [
            r"capital (is |at )?risk",
            r"you may (lose|get back less)",
            r"your (capital|money) is at risk",
        ],
        "negation_patterns": [],
        "explanation_template": (
            "An investment promotion was detected without a capital-at-risk "
            "warning, which is required under FCA COBS 4.2.1R."
        ),
        "suggestion": (
            "Add: 'Your capital is at risk. You may get back less than you invest.'"
        ),
    },

    {
        "name": "Past performance disclaimer missing",
        "fca_ref": "COBS 4.6.2R",
        "severity": 5,
        "category": "Risk Disclosure",
        "description": "Past performance cited without the mandatory FCA disclaimer.",
        "keywords": ["past performance", "historical returns", "previously delivered"],
        "regex_patterns": [
            r"\bpast performance\b",
            r"\bhistorical returns?\b",
            r"\bpreviously delivered\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "past"}, {"LOWER": "performance"}],
            [{"LOWER": "historical"}, {"LOWER": "returns"}],
        ],
        "requires_absence_of": [
            r"past performance is not a reliable indicator",
            r"past performance is not a guide",
        ],
        "negation_patterns": [],
        "explanation_template": (
            "Past performance is cited in '{match}' without the mandatory "
            "disclaimer required under FCA COBS 4.6.2R."
        ),
        "suggestion": (
            "Add immediately after any past performance reference: "
            "'Past performance is not a reliable indicator of future results.'"
        ),
    },

    # ──────────────────────────────────────────────────────────────────────
    # CATEGORY: Cost Transparency
    # ──────────────────────────────────────────────────────────────────────

    {
        "name": "Vague fee disclosure",
        "fca_ref": "COBS 6.1.9R",
        "severity": 4,
        "category": "Cost Transparency",
        "description": "Fee or charges disclosure is ambiguous or insufficiently specific.",
        "keywords": ["fees may apply", "additional costs", "charges could", "minimal fees"],
        "regex_patterns": [
            r"fees may apply",
            r"additional costs?",
            r"charges could",
            r"minimal fees",
        ],
        "spacy_patterns": [
            [{"LOWER": "fees"}, {"LOWER": "may"}, {"LOWER": "apply"}],
            [{"LOWER": "minimal"}, {"LOWER": "fees"}],
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The phrase '{match}' is vague and does not clearly explain actual "
            "costs as required under FCA COBS 6.1.9R."
        ),
        "suggestion": (
            "State specific fees clearly (e.g. '1.5% annual management charge' "
            "or '£10 monthly fee') rather than using vague language."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────
    # CATEGORY: Clarity
    # ──────────────────────────────────────────────────────────────────────

    {
        "name": "Low readability",
        "fca_ref": "COBS 4.2.1R",
        "severity": 3,
        "category": "Clarity",
        "description": "Text may be too complex for a retail customer audience.",
        "type": "readability",
        "keywords": "Low readability",
        "thresholds": {
            "flesch_reading_ease": 60,
            "fk_grade": 9,
            "max_sentence_length": 20,
        },
        "explanation_template": (
            "The text has a Flesch reading ease score of {score}, which is below "
            "the recommended threshold of 60 for retail customer communications "
            "under FCA COBS 4.2.1R."
        ),
        "suggestion": (
            "Use shorter sentences (aim for under 20 words), simpler vocabulary, "
            "and avoid complex nested clauses."
        ),
    },

    {
        "name": "Complex financial jargon",
        "fca_ref": "COBS 4.2.1R",
        "severity": 2,
        "category": "Clarity",
        "description": "Technical financial terms that may not be understood by retail customers.",
        "keywords": ["derivatives", "structured products", "hedging", "volatility"],
        "regex_patterns": [
            r"\bderivatives?\b",
            r"\bstructured products?\b",
            r"\bhedging\b",
            r"\bvolatility\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "derivatives"}],
            [{"LOWER": "structured"}, {"LOWER": "products"}],
            [{"LOWER": "hedging"}],
            [{"LOWER": "volatility"}],
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The term '{match}' may not be understood by retail customers "
            "under FCA COBS 4.2.1R, which requires clear and fair communication."
        ),
        "suggestion": (
            "Use simpler language or provide a plain English explanation "
            "immediately after the term."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────
    # CATEGORY: Fairness
    # ──────────────────────────────────────────────────────────────────────

    {
        "name": "Pressure selling language",
        "fca_ref": "CONC 3.9.4R",
        "severity": 4,
        "category": "Fairness",
        "description": "Language that pressures customers into making quick financial decisions.",
        "keywords": ["limited time", "act now", "don't miss out", "only today"],
        "regex_patterns": [
            r"\blimited time\b",
            r"\bact now\b",
            r"\bdon't miss out\b",
            r"\bonly today\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "limited"}, {"LOWER": "time"}],
            [{"LOWER": "act"}, {"LOWER": "now"}],
            [{"LOWER": "only"}, {"LOWER": "today"}],
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The phrase '{match}' may pressure customers into making quick "
            "financial decisions without adequate time to consider under "
            "FCA CONC 3.9.4R."
        ),
        "suggestion": (
            "Remove urgency language that prevents informed decision-making. "
            "Allow customers adequate time to consider their options."
        ),
    },

    {
        "name": "One-sided promotion",
        "fca_ref": "COBS 4.2.1R",
        "severity": 4,
        "category": "Fairness",
        "description": "Promotion overstates benefits without balancing risk information.",
        "keywords": ["high returns", "strong performance", "exceptional growth"],
        "regex_patterns": [
            r"\bhigh returns\b",
            r"\bstrong performance\b",
            r"\bexceptional growth\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "high"}, {"LOWER": "returns"}],
            [{"LOWER": "strong"}, {"LOWER": "performance"}],
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The content highlights '{match}' without mentioning associated "
            "risks, which is not fair and balanced under FCA COBS 4.2.1R."
        ),
        "suggestion": (
            "Include balanced information about risks and limitations alongside "
            "any benefit or performance claims."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────
    # CATEGORY: Authorisation
    # ──────────────────────────────────────────────────────────────────────

    {
        "name": "Unauthorised firm indicators",
        "fca_ref": "FSMA 2000 s.21",
        "severity": 5,
        "category": "Authorisation",
        "description": "Language suggesting the promotion may be from an unauthorised firm.",
        "keywords": ["not regulated", "unregulated", "not FCA authorised"],
        "regex_patterns": [
            r"\bnot regulated\b",
            r"\bunregulated\b",
            r"\bnot FCA[- ]authorised\b",
        ],
        "spacy_patterns": [
            [{"LOWER": "not"}, {"LOWER": "regulated"}],
            [{"LOWER": "unregulated"}],
        ],
        "negation_patterns": [],
        "explanation_template": (
            "The phrase '{match}' may indicate that this promotion is issued "
            "by or on behalf of an unauthorised firm, which violates FSMA 2000 s.21."
        ),
        "suggestion": (
            "Confirm FCA authorisation status and include the firm's FCA "
            "Firm Reference Number (FRN)."
        ),
    },
    # In fca_rules.py — add PS23/6 as a dual reference

{
    "name": "Missing mandatory crypto risk warning",
    "fca_ref": "COBS 4.12A.4R / PS23/6 para 3.14",  # ← dual reference
    "severity": 5,
    "category": "Risk Disclosure",
    "description": (
        "Cryptoasset promotions must display the FCA prescribed "
        "risk warning introduced by PS23/6 in October 2023."
    ),
    "ps23_6_requirement": (
        "PS23/6 para 3.14 requires the following warning in "
        "the specified form: 'Don't invest unless you're prepared "
        "to lose all the money you invest. This is a high-risk "
        "investment and you are unlikely to be protected if "
        "something goes wrong. Take 2 mins to learn more.'"
    ),
    "requires_absence_of": [
        r"don't invest unless you.re prepared to lose",
        r"this is a high.risk investment",
        r"unlikely to be protected if something goes wrong"
    ],
    "keywords": ["crypto", "bitcoin", "ethereum", "invest", "token"],
    "regex_patterns": [
        r"\bcrypto(asset|currency)?\b",
        r"\bbitcoin\b",
        r"\bethereum\b",
        r"\btoken\b",
    ],
    "explanation_template": (
        "Cryptoasset promotion detected without the mandatory FCA "
        "risk warning required under COBS 4.12A.4R as introduced "
        "by PS23/6."
    ),
    "suggestion": (
        "Add verbatim: 'Don't invest unless you're prepared to lose "
        "all the money you invest. This is a high-risk investment "
        "and you are unlikely to be protected if something goes "
        "wrong. Take 2 mins to learn more.'"
    ),
},
{
    "name": "Incentive to invest in cryptoassets",
    "fca_ref": "COBS 4.12A.16R / PS23/6 para 3.41",
    "severity": 5,
    "category": "Fairness",
    "description": (
        "PS23/6 explicitly prohibits monetary and non-monetary "
        "incentives to invest in cryptoassets from October 2023."
    ),
    "ps23_6_requirement": (
        "PS23/6 para 3.41: Firms must not offer any incentive "
        "to invest including referral bonuses, free crypto tokens, "
        "cashback, or any other inducement."
    ),
    "keywords": [
        "referral bonus", "free crypto", "sign-up bonus", "cashback"
    ],
    "regex_patterns": [
        r"\breferral (bonus|reward)\b",
        r"\bfree (bitcoin|crypto|token)\b",
        r"\bsign.?up bonus\b",
        r"\bcashback\b",
    ],
    "negation_patterns": [],
    "explanation_template": (
        "The phrase '{match}' constitutes an incentive to invest "
        "prohibited under COBS 4.12A.16R as introduced by PS23/6."
    ),
    "suggestion": (
        "Remove all incentives to invest. PS23/6 prohibits referral "
        "bonuses, free tokens, cashback and any other inducement "
        "to invest in cryptoassets."
    ),
},
{
    "name": "Missing cooling-off period disclosure",
    "fca_ref": "COBS 4.12A.15R / PS23/6 para 3.38",
    "severity": 4,
    "category": "Risk Disclosure",
    "description": (
        "PS23/6 requires a 24-hour cooling-off period for all "
        "direct offer financial promotions for cryptoassets."
    ),
    "ps23_6_requirement": (
        "PS23/6 para 3.38: Firms must allow a minimum 24-hour "
        "cooling-off period from the point a consumer requests "
        "to see the direct offer promotion."
    ),
    "requires_absence_of": [
        r"cooling.off",
        r"24.hour",
        r"time to reflect",
    ],
    "keywords": ["invest now", "buy now", "get started"],
    "regex_patterns": [
        r"\binvest now\b",
        r"\bbuy now\b",
        r"\bopen (an )?account\b",
    ],
    "explanation_template": (
        "Direct offer crypto promotion detected without the mandatory "
        "24-hour cooling-off period required by PS23/6 para 3.38."
    ),
    "suggestion": (
        "Add: 'You have a 24-hour cooling-off period before your "
        "investment is processed. This is required by FCA rules "
        "introduced in October 2023.'"
    ),
},
{
    "name": "Missing appropriateness assessment disclosure",
    "fca_ref": "COBS 10.1.2R / PS23/6 para 3.45",
    "severity": 4,
    "category": "Risk Disclosure",
    "description": (
        "PS23/6 requires firms to conduct and disclose an "
        "appropriateness assessment before a retail consumer "
        "can invest in cryptoassets."
    ),
    "ps23_6_requirement": (
        "PS23/6 para 3.45: Firms must assess whether a retail "
        "consumer has the knowledge and experience to understand "
        "the risks of investing in cryptoassets before allowing "
        "them to proceed."
    ),
    "requires_absence_of": [
        r"appropriateness (assessment|check|test)",
        r"knowledge and experience",
        r"understand the risks",
    ],
    "keywords": ["invest", "buy", "purchase", "get started"],
    "regex_patterns": [
        r"\bstart investing\b",
        r"\bbuy (bitcoin|crypto|ethereum)\b",
        r"\bopen (an )?account\b",
    ],
    "explanation_template": (
        "Crypto promotion directs consumers to invest without "
        "disclosing the appropriateness assessment requirement "
        "under PS23/6 para 3.45."
    ),
    "suggestion": (
        "Add: 'Before investing, we are required to assess whether "
        "cryptoasset investment is appropriate for you based on "
        "your knowledge and experience.'"
    ),
},
]
   
   
   


# "difficult_words": textstat.difficult_words(text) # type: ignore
def check_readability(text, rule):
    scores = {
        "flesch": textstat.flesch_reading_ease(text), # type: ignore
        "fk_grade": textstat.flesch_kincaid_grade(text),# type: ignore
        "sentence_length": textstat.avg_sentence_length(text), # type: ignore
        
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
                    "start": 0,
                    "end": len(text),
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






