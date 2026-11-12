#!/usr/bin/env python3
"""Small-open-model evaluation on the certified benchmark (fixed seed, one puzzle per call)."""
import json, random, urllib.request, statistics

BENCHMARK = "benchmark/puzzles.jsonl"
URL = "http://localhost:8080/v1/chat/completions"  # vLLM serving endpoint
MODEL = "SZLHOLDINGS/SZL-Nemotron-Mini-4B-Estate-v1"
SEED = 3407

def main():
    with open(BENCHMARK) as f:
        puzzles = [json.loads(l) for l in f]
    random.seed(SEED)
    fair = [p for p in puzzles if p["level"] <= 3]
    sample = []
    for fam in ["zebra", "sudoku", "killer", "futoshiki"]:
        fam_p = [p for p in fair if p["family"] == fam]
        sample += random.sample(fam_p, min(3, len(fam_p)))

    def solve(p):
        body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": p["prompt"] + "\n\n" + p["answer_format"]}], "max_tokens": 1500}).encode()
        req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=240) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]

    def score(p, out):
        if not out:
            return 0.0
        sol = p["solution"]; text = out.lower()
        if p["family"] == "zebra":
            correct = total = 0
            for value, house in sol.items():
                total += 1
                if str(house) in text and value in text:
                    correct += 1
            return correct / max(total, 1)
        digits = [str(v) for v in sol] if isinstance(sol, list) else []
        return sum(1 for d in digits if d in text) / len(digits) if digits else 0.0

    results = []
    for p in sample:
        out = solve(p)
        results.append({"id": p["id"], "family": p["family"], "level": p["level"],
                        "cell_accuracy_crude": round(score(p, out), 3),
                        "output_excerpt": out[:300]})
    by_fam = {}
    for r in results:
        by_fam.setdefault(r["family"], []).append(r["cell_accuracy_crude"])
    print(json.dumps({f: round(statistics.mean(v), 3) for f, v in by_fam.items()}, indent=1))

if __name__ == "__main__":
    main()
