#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

expected_comment="JasperReports Library version 6.20.6"
error_found=0

while IFS= read -r -d '' file; do
  if ! grep -q "$expected_comment" "$file"; then
    echo "❌ $file: Expected $expected_comment" >&2
    error_found=1
  fi
done < <(find "$repo_root" -name "*.jrxml" -print0)

if [ "$error_found" -ne 0 ]; then
  echo "Found JRXML files not built with $expected_comment" >&2
  exit 1
fi

echo "All JRXML files use $expected_comment"
