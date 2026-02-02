from pathlib import Path
from tqdm import tqdm
import argparse

r".venv\Scripts\Activate.ps1"

def is_email_content(path: Path) -> bool:

    try:
        with open(path, "rb") as f:
            chunk = f.read(2048)  # read first 2KB only

        # Decode safely (emails are mostly ASCII / latin-1)
        text = chunk.decode("utf-8", errors="ignore")

        headers = (
            "from:",
            "to:",
            "subject:",
            "date:",
            "message-id:",
        )

        text_lower = text.lower()

        return any(h in text_lower for h in headers)

    except Exception:
        # If we can't read it at all, treat as non-email
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--maildir", required=True, help=r'Path like "C:\enron\maildir"')
    args = parser.parse_args()

    root = Path(args.maildir)
    print("Scanning:", root.resolve())

    if not root.exists():
        print(f"ERROR: maildir not found: {root}")
        raise SystemExit(2)

    all_files = [p for p in root.rglob("*") if p.is_file()]

    candidates = []
    for p in all_files:
        if p.name.startswith("."):
            continue
        if p.stat().st_size < 50:
            continue
        candidates.append(p)

    print("Total files:", len(all_files))
    print("Candidate email-like files:", len(candidates))

    print("\nSample candidates:")
    for p in candidates[:10]:
        print(" -", p)

    email_files = []

    print(f"Starting content inspection on {len(candidates)} files...")

    for p in tqdm(
        candidates,
        desc="Inspecting content (email detection)",
        unit="file",
    ):
        if is_email_content(p):
            email_files.append(p)

    print(f"\nContent inspection complete.")
    print(f"Confirmed email files: {len(email_files)}")

if __name__ == "__main__":
    main()
