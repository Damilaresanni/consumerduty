from deepeval.test_case import LLMTestCase
from deepeval import evaluate
from deepeval.test_case import LLMTestCaseParams
from datetime import datetime
import json
import csv, os

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    GEval
)

def evalFca(query,answer,chunks,findings):
    
    
    test_case = LLMTestCase(
        input = query,
        actual_output=answer,
        expected_output="NON_COMPLIANT. The phrase 'guaranteed 10% annual returns' violates FCA CONC 3.3.1R.",
        retrieval_context=chunks,
        context=str(
        findings.values_list("rule_name", "description", "snippet", "severity"))
        )

    compliance_metric = GEval(
        name="Compliance Accuracy",
        criteria="Check if the output correctly identifies FCA compliance violations and cites the relevant rule.",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT
        ],
        threshold=0.7
    )
    

    answer_relevancy = AnswerRelevancyMetric(threshold=0.7)
    faithfulness = FaithfulnessMetric(threshold=0.8)
    hallucination = HallucinationMetric(threshold=0.3)
    contextual_precision = ContextualPrecisionMetric(threshold=0.7)
    contextual_recall = ContextualRecallMetric(threshold=0.7)
    
    results = evaluate(
    test_cases=[test_case],
    metrics=[answer_relevancy, faithfulness, 
            compliance_metric,hallucination,
            contextual_precision,
            contextual_recall]
    )
    
    save_eval_result(test_case, results)
    
    output = {
    "timestamp": datetime.now().isoformat(),
    "test_input": test_case.input,
    "actual_output": test_case.actual_output,
    "expected_output": test_case.expected_output,
    "retrieval_context": test_case.retrieval_context,  # PDF chunks
    "context": test_case.context,                      # FCA rule-based findings
    "results": []
    }
    
    for metric in results.test_results[0].metrics_data:
        output["results"].append({
            "metric": metric.name,
            "score": round(metric.score, 4),
            "passed": metric.passed,
            "reason": metric.reason,
            "threshold": metric.threshold
        })

    # Save to file
    filename_json = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename_json, "w") as f:
        json.dump(output, f, indent=2)
        
        
        
        
    filename_csv = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "input", "actual_output",
            "metric", "score", "passed", "threshold", "reason"
        ])
        for metric in results.test_results[0].metrics_data:
            writer.writerow([
                datetime.now().isoformat(),
                test_case.input,
                test_case.actual_output,
                metric.name,
                round(metric.score, 4),
                metric.passed,
                metric.threshold,
                metric.reason
            ])

    print(f"Saved to {filename_json}")
    print(f"Saved to {filename_csv}")
    
    
    

RESULTS_FILE = "evals/eval_results.json"

def save_eval_result(test_case, results):
    os.makedirs("evals", exist_ok=True)

    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            all_results = json.load(f)
    else:
        all_results = []

    record = {
        "timestamp": datetime.now().isoformat(),
        "input": test_case.input,
        "actual_output": test_case.actual_output,
        "expected_output": test_case.expected_output,
        "retrieval_context": test_case.retrieval_context,  # PDF chunks
        "context": test_case.context,                       # FCA rule findings
        "metrics": []
    }

    for metric in results.test_results[0].metrics_data:
        record["metrics"].append({
            "name": metric.name,
            "score": round(metric.score, 4),
            "passed": metric.passed,
            "threshold": metric.threshold,
            "reason": metric.reason
        })

    all_results.append(record)

    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"Saved {len(record['metrics'])} metrics to {RESULTS_FILE}")





        