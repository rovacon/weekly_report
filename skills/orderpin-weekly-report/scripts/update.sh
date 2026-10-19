#!/usr/bin/env bash
set -euo pipefail

# Resolve the real checkout even when invoked through an installed skill symlink.
repo_dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd -- "$repo_dir"
[[ "$(git rev-parse --show-toplevel)" == "$repo_dir" ]] || {
  echo "Skill must live in its own weekly_report Git checkout." >&2; exit 1;
}
case "$(git config --get remote.origin.url)" in
  https://github.com/rovacon/weekly_report.git|https://github.com/rovacon/weekly_report|git@github.com:rovacon/weekly_report.git) ;;
  *) echo "Refusing to update from an unexpected origin." >&2; exit 1 ;;
esac
[[ "$(git symbolic-ref --quiet --short HEAD)" == "main" ]] || {
  echo "Switch to main after preserving your work; no branch was changed." >&2; exit 1;
}
[[ -z "$(git status --porcelain --untracked-files=all)" ]] || {
  echo "Local changes found. Preserve them before updating; nothing was overwritten." >&2; exit 1;
}
git fetch --no-tags origin main
[[ "$(git rev-list --count FETCH_HEAD..HEAD)" == "0" ]] || {
  echo "Local-only commits found. Resolve them before running the weekly skill." >&2; exit 1;
}
git merge --ff-only FETCH_HEAD
