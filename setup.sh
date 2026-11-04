#!/usr/bin/env bash
# =======================================================
# Zack D. Films 3D Explainer — Automated Linux / macOS Setup
# =======================================================

set -e

echo ""
echo "======================================================="
echo "   ZACK D. FILMS 3D EXPLAINER - ONE-CLICK UNIX SETUP"
echo "======================================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in your PATH."
    echo "Please install Python 3.10+."
    exit 1
fi

python3 setup.py
echo ""
echo "Setup finished successfully!"

