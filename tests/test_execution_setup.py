"""Offline regressions for startup and attachment resolution."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_help_without_credentials(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c", """
import os, runpy, socket, sys
from unittest.mock import patch
for key in ('OPENAI_API_KEY', 'HF_TOKEN'):
    os.environ.pop(key, None)
os.environ['ANONYMIZED_TELEMETRY'] = 'false'
sys.path.insert(0, sys.argv[1])
runner = sys.argv[1] + '/run_hist.py'
sys.argv = [runner, '--help']
with patch('dotenv.load_dotenv'), patch.object(socket.socket, 'connect', side_effect=AssertionError('Unexpected network access')):
    runpy.run_path(runner, run_name='__main__')
""", str(ROOT)],
        cwd=tmp_path, capture_output=True, text=True, timeout=90,
    )
    assert result.returncode == 0, result.stderr
    assert "--dataset-path" in result.stdout
    assert "--files-dir" in result.stdout


def test_attachment_directory(tmp_path):
    from dataset_loader import load_custom_dataset
    workbook = tmp_path / "HistBench.xlsx"
    attachment = tmp_path / "001.png"
    attachment.write_bytes(b"fixture")
    pd.DataFrame([{
        "ID": 1, "Question": "Read the image", "Answer": "fixture",
        "Data Requirements": attachment.name, "Answer Type": "text", "Level": 1,
    }]).to_excel(workbook, sheet_name="level 1", index=False)
    with contextlib.redirect_stdout(io.StringIO()):
        dataset = load_custom_dataset(str(workbook), files_dir=str(workbook.parent), sheet_name="level 1")
    assert len(dataset) == 1
    assert dataset[0]["file_name"] == str(attachment)
    assert dataset[0]["file_names"] == [str(attachment)]


def test_main_reports_missing_key(monkeypatch):
    import run_hist
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setattr(sys, "argv", ["run_hist.py", "--run-name", "check"])
    with pytest.raises(SystemExit, match="Missing OPENAI_API_KEY"):
        run_hist.main()


def test_main_reports_missing_dataset(monkeypatch, tmp_path):
    import run_hist
    monkeypatch.setenv("OPENAI_API_KEY", "local-test-placeholder")
    monkeypatch.setattr(sys, "argv", ["run_hist.py", "--run-name", "check", "--dataset-path", str(tmp_path / "missing.xlsx")])
    with pytest.raises(SystemExit, match="Dataset not found"):
        run_hist.main()
