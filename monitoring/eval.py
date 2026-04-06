# ==========================================
# FCA COMPLIANCE EVALUATION PIPELINE (ENHANCED)
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .nlp import run_spacy_rules

# -----------------------------
# 1. LOAD DATASET
# -----------------------------

def load_dataset(path):
    df = pd.read_csv(path)
    return df.to_dict(orient="records")

# -----------------------------
# 2. MOCK RULE ENGINE (REPLACE)
# -----------------------------

def run_spacy_rules(text):
    findings = []

    if "guaranteed" in text.lower() or "no risk" in text.lower():
        findings.append({"rule": "Guarantee-like Wording", "severity": "high"})

    if "fees may apply" in text.lower():
        findings.append({"rule": "Unclear Fees", "severity": "medium"})

    return findings

# -----------------------------
# 3. RISK SCORING ENGINE
# -----------------------------

def calculate_risk(findings):
    score = 0

    for f in findings:
        if f["severity"] == "high":
            score += 3
        elif f["severity"] == "medium":
            score += 2
        else:
            score += 1

    return score


def normalize_score(score):
    if score >= 3:
        return "HIGH"
    elif score == 2:
        return "MEDIUM"
    else:
        return "LOW"

# -----------------------------
# 4. MAIN EVALUATION FUNCTION
# -----------------------------

def evaluate_system(test_data):
    y_true = []
    y_pred = []
    results = []

    for sample in test_data:
        text = sample["text"]
        true_label = sample["label"]

        findings = run_spacy_rules(text)
        score = calculate_risk(findings)
        pred_label = normalize_score(score)

        y_true.append(true_label)
        y_pred.append(pred_label)

        results.append({
            "text": text,
            "true_label": true_label,
            "predicted_label": pred_label,
            "findings": findings
        })

    return y_true, y_pred, results

# -----------------------------
# 5. CONFUSION MATRIX VISUALIZATION
# -----------------------------

def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred, labels=["LOW", "MEDIUM", "HIGH"])

    plt.figure()
    plt.imshow(cm)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.xticks([0,1,2], ["LOW","MEDIUM","HIGH"])
    plt.yticks([0,1,2], ["LOW","MEDIUM","HIGH"])

    for i in range(len(cm)):
        for j in range(len(cm[0])):
            plt.text(j, i, cm[i][j], ha='center', va='center')

    plt.savefig("confusion_matrix.png")
    plt.close()

# -----------------------------
# 6. FALSE POSITIVE / NEGATIVE ANALYSIS
# -----------------------------

def error_analysis(results):
    false_positives = []
    false_negatives = []

    for r in results:
        if r["predicted_label"] != r["true_label"]:
            if r["predicted_label"] > r["true_label"]:
                false_positives.append(r)
            else:
                false_negatives.append(r)

    return false_positives, false_negatives

# -----------------------------
# 7. LLM FAITHFULNESS CHECK
# -----------------------------

def evaluate_faithfulness(llm_output, findings):
    grounded = 0

    for f in findings:
        if f["rule"].lower() in llm_output.lower():
            grounded += 1

    if len(findings) == 0:
        return 1.0

    return grounded / len(findings)

# -----------------------------
# 8. SAVE RESULTS TO PDF
# -----------------------------

def save_to_pdf(report_text, filename="evaluation_report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    for line in report_text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 10))

    doc.build(content)

# -----------------------------
# 9. RUN PIPELINE
# -----------------------------

if __name__ == "__main__":

    data = load_dataset("fca_dataset_50_samples.csv")

    y_true, y_pred, results = evaluate_system(data)

    # Metrics
    report = classification_report(y_true, y_pred)
    print(report)

    # Confusion matrix
    plot_confusion_matrix(y_true, y_pred)

    # Error analysis
    fp, fn = error_analysis(results)

    print("\nFalse Positives:", len(fp))
    print("False Negatives:", len(fn))

    # Example LLM evaluation
    example_output = "This contains guarantee-like wording which may be misleading."
    faithfulness_score = evaluate_faithfulness(example_output, results[0]["findings"])

    print("\nFaithfulness Score:", faithfulness_score)

    # Save report
    full_report = f"""
FCA Compliance Evaluation Report

Classification Report:
{report}

False Positives: {len(fp)}
False Negatives: {len(fn)}

Faithfulness Score (example): {faithfulness_score}
"""

    save_to_pdf(full_report)

# ==========================================
# END OF PIPELINE
# ==========================================
