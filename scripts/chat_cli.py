import argparse
import sys
import urllib.parse
import urllib.request


def request_chat(base_url: str, line: str, mode: str | None, reset: bool, timeout_s: float) -> str:
    params: dict[str, str] = {"line": line}
    if mode and mode != "auto":
        params["mode"] = mode
    if reset:
        params["reset"] = "true"

    url = f"{base_url.rstrip('/')}/chat?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.read().decode("utf-8", errors="replace")


HELP = """Commands:
  /help                 Show this help
  /exit, /quit          Exit
  /reset                Clear server-side chat history
  /mode chat|qa|auto    Switch mode

Notes:
  - mode=chat: chitchat model
  - mode=qa: document QA (Elasticsearch)
  - mode=auto: let classifier decide
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Interactive chat client for chitchat_api")
    parser.add_argument("--base-url", default="http://127.0.0.1:3000", help="API base URL")
    parser.add_argument(
        "--mode",
        default="qa",
        choices=["auto", "chat", "qa"],
        help="Initial mode (default: qa)",
    )
    parser.add_argument("--timeout", type=float, default=60.0, help="Per-request timeout seconds")
    parser.add_argument(
        "--reset-on-start",
        action="store_true",
        help="Reset server history once when starting",
    )
    args = parser.parse_args()

    base_url: str = args.base_url
    mode: str = args.mode
    timeout_s: float = args.timeout

    print(f"Connected to {base_url} (mode={mode})")
    print("Type your message. Use /help for commands.")

    reset_next = bool(args.reset_on_start)

    while True:
        try:
            user = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return 0

        if not user:
            continue

        if user.startswith("/"):
            cmd = user[1:].strip().lower()
            if cmd in {"exit", "quit"}:
                print("bye")
                return 0
            if cmd == "help":
                print(HELP)
                continue
            if cmd == "reset":
                reset_next = True
                print("(ok) will reset on next message")
                continue
            if cmd.startswith("mode"):
                parts = cmd.split()
                if len(parts) != 2 or parts[1] not in {"auto", "chat", "qa"}:
                    print("Usage: /mode chat|qa|auto")
                    continue
                mode = parts[1]
                print(f"(ok) mode={mode}")
                continue

            print("Unknown command. Use /help")
            continue

        try:
            answer = request_chat(
                base_url=base_url,
                line=user,
                mode=mode,
                reset=reset_next,
                timeout_s=timeout_s,
            ).strip()
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {type(exc).__name__}: {exc}")
            reset_next = False
            continue

        reset_next = False
        sys.stdout.write(answer + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    raise SystemExit(main())
