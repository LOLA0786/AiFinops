#!/bin/bash
set -e

echo "[1] Creating venv..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2] Installing dev dependencies..."
pip install --upgrade pip
pip install pre-commit black flake8 detect-secrets git-lfs

echo "[3] Installing git LFS..."
git lfs install

echo "[4] Installing pre-commit hooks..."
pre-commit install

echo "[5] Done! Dev environment ready."
