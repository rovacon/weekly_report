#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
target_dir="${HOME}/.agents/skills"
if [[ $# -gt 0 ]]; then
  if [[ $# -ne 2 || "$1" != "--target" || -z "$2" ]]; then
    echo "Usage: bash scripts/install.sh [--target /path/to/skills]" >&2
    exit 2
  fi
  target_dir="$2"
fi
skill_dir="$repo_dir/skills/orderpin-weekly-report"
[[ -f "$skill_dir/SKILL.md" ]] || { echo "Missing SKILL.md" >&2; exit 1; }
mkdir -p -- "$target_dir"
target_dir="$(cd -P -- "$target_dir" && pwd)"
destination="$target_dir/orderpin-weekly-report"
if [[ -L "$destination" && "$(readlink "$destination")" == "$skill_dir" ]]; then
  echo "Already installed: $destination"
elif [[ -e "$destination" || -L "$destination" ]]; then
  echo "Refusing to overwrite existing skill: $destination" >&2
  exit 1
else
  ln -s -- "$skill_dir" "$destination"
  echo "Installed: $destination -> $skill_dir"
fi
echo "Reopen your Agent session and use \$orderpin-weekly-report."
