#!/usr/bin/env bash
set -euo pipefail
trap 'echo "❌ Error on line $LINENO at command: $BASH_COMMAND"; exit 1' ERR

# ------------------------------------------------------------------
# Load environment variables safely
# ------------------------------------------------------------------
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs/scraping"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/scraper.log"

# ------------------------------------------------------------------
# Run Telegram scraper
# ------------------------------------------------------------------
echo "🟢 Starting Telegram scraping..."
python -m medi_tg_analytics.scraping.scraper 2>&1 | tee -a "$LOG_FILE"
echo "✅ Scraping finished, logs saved to $LOG_FILE"
