"""Check local execution prerequisites without making service API calls."""

import argparse
import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-credentials", action="store_true")
    args = parser.parse_args()
    failures = []

    def report(name, ok, detail=""):
        print(f"{'OK' if ok else 'FAIL'}: {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    report("Python 3.12+", sys.version_info >= (3, 12), sys.version.split()[0])
    os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")
    for name in ("dotenv", "pandas", "openpyxl", "torch", "torchvision", "smolagents",
                 "litellm", "pdfminer.high_level", "browser_use", "scripts.text_inspector_tool"):
        try:
            module = importlib.import_module(name)
            if name == "dotenv":
                module.load_dotenv(ROOT / ".env")
            if name == "browser_use":
                assert Path(module.__file__).resolve().is_relative_to(ROOT / "browser_use"), "Must use the bundled browser_use"
            report(name, True)
        except Exception as exc:
            report(name, False, str(exc))

    result = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
    report("Dependency consistency", result.returncode == 0, result.stdout.strip())
    for command in ("git", "git-lfs", "ffmpeg", "pdftoppm"):
        report(command, shutil.which(command) is not None)

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content("<title>HistAgent readiness</title>")
            assert page.title() == "HistAgent readiness"
            browser.close()
        report("Headless Chromium", True)
    except Exception as exc:
        report("Headless Chromium", False, str(exc))

    workbook = ROOT / "HistBench" / "HistBench.xlsx"
    try:
        import pandas as pd
        sheets = pd.read_excel(workbook, sheet_name=None)
        report("HistBench workbook", any(not sheet.empty for sheet in sheets.values()),
               f"{sum(len(sheet) for sheet in sheets.values())} rows")
        pointers = []
        for path in workbook.parent.iterdir():
            if path.is_file():
                with path.open("rb") as file:
                    if file.read(43).startswith(b"version https://git-lfs.github.com/spec/v1"):
                        pointers.append(path.name)
        report("Dataset LFS files downloaded", not pointers, f"{len(pointers)} unresolved pointers")
    except Exception as exc:
        report("HistBench workbook", False, str(exc))

    for key in ("OPENAI_API_KEY", "SERPAPI_API_KEY"):
        configured = bool(os.getenv(key))
        if args.require_credentials:
            report(key, configured, "configured" if configured else "set in .env")
        else:
            print(f"{'OK' if configured else 'TODO'}: {key} — {'configured' if configured else 'set in .env before execution'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
