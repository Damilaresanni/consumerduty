from deepeval.test_case import LLMTestCase
from deepeval import evaluate
from deepeval.test_case import LLMTestCaseParams
from datetime import datetime
import json
import csv, os
from celery.result import AsyncResult
from celery import shared_task

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    GEval
)

RESULTS_FILE = "evals/eval_results1.json"

def save_eval_result(test_case, results,output):
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
        "retrieval_context": test_case.retrieval_context,
        "context": test_case.context,
        "metrics": []
    }

    for metric in results.test_results[0].metrics_data:
        
        score     = round(metric.score, 4)
        threshold = metric.threshold
        
        if metric.name == "Hallucination":
            passed = score <= threshold
        else:
            passed = score >= threshold

        record["metrics"].append({
            "name":      metric.name,
            "score":     score,
            "threshold": threshold,
            "passed":    passed,           
            "reason":    metric.reason
        })

    all_results.append(record)

    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"Saved {len(record['metrics'])} metrics to {RESULTS_FILE}")

    for metric in results.test_results[0].metrics_data:
        output["results"].append({
            "metric": metric.name,
            "score": round(metric.score, 4),
            "passed": metric.success,
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
                metric.success,
                metric.threshold,
                metric.reason
            ])

    print(f"Saved to {filename_json}")
    print(f"Saved to {filename_csv}")

    return results


        


