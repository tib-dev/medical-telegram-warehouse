#!/bin/bash
# ==========================================================
# run_load_to_db.sh
# Script to load raw Telegram JSON data into PostgreSQL
# ==========================================================

# Exit immediately if a command exits with a non-zero status
set -e


# Optional: load environment variables from .env
if [ -f ".env" ]; then
    echo "Loading environment variables..."
    export $(grep -v '^#' .env | xargs)
fi

# Run the Python loader
echo "Starting raw data load to PostgreSQL..."
python -m medi_tg_analytics.loading.load_raw_to_postgres

echo "✅ Raw data load completed successfully!"
