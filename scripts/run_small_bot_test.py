import argparse
import csv
import random
import time
import urllib.parse
import urllib.request


def call_chat_api(
    base_url: str,
    question: str,
    mode: str | None,
    timeout_s: float,
) -> str:
    params: dict[str, str] = {
        "line": question,
        "reset": "true",
    }
    if mode:
        params["mode"] = mode

    url = f"{base_url.rstrip('/')}/chat?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method="GET")

    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run chitchat_api on small_bot_test.csv")
    parser.add_argument(
        "--input",
        default="small_bot_test.csv",
        help="Input CSV path (default: small_bot_test.csv)",
    )
    parser.add_argument(
        "--output",
        default="small_bot_result-3.csv",
        help="Output CSV path (default: small_bot_result-3.csv)",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:3000",
        help="API base URL (default: http://127.0.0.1:3000)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Per-request timeout seconds (default: 60)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="If > 0, randomly sample N rows (default: 0 = run all)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used with --sample (default: 42)",
    )

    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if args.sample and args.sample > 0:
        random.seed(args.seed)
        rows = random.sample(rows, k=min(args.sample, len(rows)))

    out_rows: list[dict[str, str]] = []

    for row in rows:
        q_id = (row.get("id") or "").strip()
        mode = (row.get("mode") or "").strip().lower() or None
        question = (row.get("question") or "").strip()

        t0 = time.perf_counter()
        try:
            answer = call_chat_api(
                base_url=args.base_url,
                question=question,
                mode=mode,
                timeout_s=args.timeout,
            ).strip()
        except Exception as exc:  # noqa: BLE001
            answer = f"ERROR: {type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - t0

        out_rows.append(
            {
                "id": q_id,
                "answer": answer,
                "time": f"{elapsed:.6f}",
            }
        )

        print(f"{q_id}: {mode or ''} {elapsed:.2f}s")

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "answer", "time"])
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
