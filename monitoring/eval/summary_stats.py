import json
import statistics

with open("evals/eval_results_summary.json") as f:
    all_results = json.load(f)

# Group scores by metric name
from collections import defaultdict
metric_scores = defaultdict(list)

for record in all_results:
    for m in record["metrics"]:
        metric_scores[m["name"]].append(m["score"])

print(f"{'Metric':<30} {'N':>4} {'Mean':>6} {'Min':>6} {'Max':>6} {'Pass Rate':>10}")
print("-" * 65)
for name, scores in metric_scores.items():
    passed = [s for s in scores if s >= 0.7]  # adjust threshold
    print(f"{name:<30} {len(scores):>4} {statistics.mean(scores):>6.3f} "
          f"{min(scores):>6.3f} {max(scores):>6.3f} "
          f"{len(passed)/len(scores)*100:>9.1f}%")