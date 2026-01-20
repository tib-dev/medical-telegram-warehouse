#!/usr/bin/env bash
# ==========================================================
# run_yolo.sh
# Run YOLOv8 image enrichment for Telegram data
# ==========================================================

set -euo pipefail

echo "🚀 Starting YOLOv8 image detection..."

python -m medi_tg_analytics.enrichment.yolo_detect

echo "✅ YOLO detection completed. Results saved to CSV."
