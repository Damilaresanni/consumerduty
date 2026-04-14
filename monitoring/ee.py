def build_compliance_prompt(query, retrieval_context, context, is_crypto=False):

    base_system_prompt = """You are an FCA compliance reviewer specialising
in financial promotion compliance. You assess whether financial promotions
comply with FCA rules and return structured verdicts.

Always return your response in exactly this format:
Label: COMPLIANT or NON_COMPLIANT
Violations: [list each violation found, or 'None']
FCA Rules Breached: [list specific rule references, or 'None']
Reason: [explain each violation with the specific rule reference]
Suggestion: [how to make the promotion compliant]"""

    # Add PS23/6 context for crypto queries
    crypto_addendum = """

IMPORTANT — CRYPTOASSET PROMOTIONS:
This promotion relates to cryptoassets and is subject to the FCA's
cryptoasset financial promotion rules introduced by PS23/6 in October 2023.

You must specifically check for:
1. Mandatory risk warning (COBS 4.12A.4R / PS23/6 para 3.14):
   Must include verbatim: "Don't invest unless you're prepared to lose
   all the money you invest. This is a high-risk investment and you are
   unlikely to be protected if something goes wrong."

2. No incentives to invest (COBS 4.12A.16R / PS23/6 para 3.41):
   Referral bonuses, free tokens, cashback and all other inducements
   are prohibited.

3. Cooling-off period (COBS 4.12A.15R / PS23/6 para 3.38):
   Direct offer promotions must disclose the 24-hour cooling-off period.

4. Appropriateness assessment (COBS 10.1.2R / PS23/6 para 3.45):
   Firms must assess consumer knowledge and experience before allowing
   investment.

5. FCA registration or approval (FSMA 2000 s.21 / PS23/6):
   The promotion must be made by or approved by an FCA registered or
   authorised firm. The FCA registration number must be stated.

If any of the above are missing or violated, the promotion is
NON_COMPLIANT regardless of other content."""

    system_prompt = (
        base_system_prompt + crypto_addendum
        if is_crypto
        else base_system_prompt
    )

    user_prompt = f"""
Rule-based findings (from FCA rule engine):
{chr(10).join(context) if context else 'No rule-based findings.'}

Retrieved document sections and regulatory reference:
{chr(10).join(retrieval_context) if retrieval_context else 'No context retrieved.'}

Financial promotion text to assess:
{query}

Provide your compliance verdict:"""

    return system_prompt, user_prompt