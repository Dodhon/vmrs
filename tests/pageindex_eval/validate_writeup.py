from pathlib import Path
import sys

REQUIRED_SECTIONS = [
    "What problem PageIndex solves",
    "Fit with Neo4j KG + MCP architecture",
    "Traceability / grounding",
    "Minimal PoC",
    "Tradeoffs",
    "Recommendation",
]

DOC_PATH = Path(__file__).resolve().parents[2] / "docs" / "pageindex_eval" / "README.md"


def main() -> int:
    if not DOC_PATH.exists():
        print(f"FAIL: Missing write-up at {DOC_PATH}")
        return 1

    text = DOC_PATH.read_text()
    missing = [s for s in REQUIRED_SECTIONS if s not in text]
    if missing:
        print("FAIL: Missing required sections:")
        for m in missing:
            print(f"- {m}")
        return 1

    print("PASS: All required sections present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
