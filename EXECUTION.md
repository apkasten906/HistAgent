# Run HistAgent

Run these commands from the repository root in the supplied Python 3.12
devcontainer. See [.devcontainer/README.md](.devcontainer/README.md) to rebuild it.

1. Copy `.env.example` to `.env` if `.env` does not already exist. Set
   `OPENAI_API_KEY` and `SERPAPI_API_KEY` in `.env`. The file is ignored by Git.
   Add optional service keys when enabling their tools.
2. Download the public dataset if it is not present:

   ```bash
   git clone https://huggingface.co/datasets/jiahaoq/HistBench HistBench
   git -C HistBench lfs pull
   ```

3. Check dependencies, Chromium, the workbook, LFS downloads, and credentials:

   ```bash
   python scripts/check_environment.py --require-credentials
   python run_hist.py --help
   ```

   Omit `--require-credentials` to check the environment before adding keys.
   The checks do not call model APIs or validate keys with providers.

4. Start with one question (this makes billable model and search requests):

   ```bash
   python run_hist.py --run-name first_run --level level1 --question-ids 5 --concurrency 1 --no-springer
   ```

   Question 5 is a text-only Level 1 question. For another question, use its ID from `HistBench/HistBench.xlsx` and the
   matching difficulty level. Use a new run name for each experiment to avoid
   the existing-results prompt. Results go to
   `output/level1_final_summary/first_run.jsonl` with related reports and logs.

The runner defaults to `gpt-4o`; use `--model-id` to select another compatible
model. Add `--use-image-agent`, `--use-file-agent`, `--use-literature-agent`,
or `--use-browser` as needed. Omit `--no-springer` after configuring Springer
and LlamaParse credentials. OCR and other specialist tools need their respective
keys from `.env.example`.

The default workbook is `HistBench/HistBench.xlsx` beside the runner, and
attachments are resolved relative to that workbook. For another location, use
`--dataset-path /path/to/HistBench.xlsx` and optionally
`--files-dir /path/to/attachments`.

## GitHub connection

The expected `origin` is `https://github.com/apkasten906/HistAgent.git`.
Verify it with `git remote -v` and refresh remote references with `git fetch origin`.
Public fetches do not require authentication. To enable authenticated GitHub CLI
operations and pushes, run `gh auth login` followed by `gh auth setup-git` in your
terminal, then verify with `gh auth status`. Existing host Git credentials may
also provide push access. No application API keys belong in Git.
