#!/usr/bin/env bash
set -euo pipefail

pip install -r test_requirements.txt

pytest /app/tests/ --cov=. --cov-fail-under=60
python /app/config/ci/generate_coverage_badge.py
