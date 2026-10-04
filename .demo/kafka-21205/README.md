# KAFKA-21205 formatter demonstration

This is a fork-only demonstration for https://github.com/apache/kafka/pull/23691.
It is not intended for merging into Apache Kafka.

## Exact source versions

- `old-pr-format.py`: `.github/scripts/pr-format.py` from Apache Kafka commit
  `96e9416e4f4bb5321e58c87914ef1c20590de894` (the fix PR's base snapshot).
- `fixed-pr-format.py`: the same path from fix PR commit
  `66ba3415a36ba7bb39aaf1d80a76785e513991ef`.
- Both scripts are copied without modifications. The harness invokes their
  complete CLI entry points, including the GitHub description-edit path.

## What the live workflow does

1. Restores `input.md` as this test PR's description.
2. Runs the original script and saves the resulting broken description.
3. Restores exactly the same input.
4. Runs the fixed script twice, verifies exact preservation and idempotence,
   and checks its log message reporting that no rewrite is needed.
5. Uploads descriptions, a before diff, and complete CLI logs as an artifact.
   The final PR description displays the intact input.

The workflow is restricted to `demo/kafka-21205-markdown` in `gitedmond/kafka`.
It never edits the upstream fix PR. It uses an isolated base branch because
Kafka's normal `workflow_run` linter takes its code from the default branch.

## Reproduce locally

```sh
python -m pip install markdown-it-py==4.2.0
python .demo/kafka-21205/run-demo.py --local
```

Local mode substitutes only the `gh` CLI reads/writes with a file-backed
description. The old and fixed formatter scripts themselves run unchanged.
Checked-in `local-results/` files were produced by this mode, not by GitHub
Actions. Live results, when available, are in the workflow artifact and summary.
