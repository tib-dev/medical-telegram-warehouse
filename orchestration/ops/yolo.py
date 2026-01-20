from dagster import op, In, Nothing, OpExecutionContext
from medi_tg_analytics.core.project_root import get_project_root
from medi_tg_analytics.core.settings import settings
import subprocess
import sys
import os

root = get_project_root()
logs_dir = settings.paths.LOGS["dagster_logs_dir"]
logs_dir.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------
# RUN YOLO ENRICHMENT
# -------------------------------------------------------


@op(ins={"start": In(Nothing)})
def run_yolo_enrichment(context: OpExecutionContext):
    """
    Enrich scraped Telegram images using YOLO-based detection.
    """
    log_file = logs_dir / "yolo_enrichment.log"
    script_path = root / "src"/"medi_tg_analytics"/"enrichment"/"yolo_detect.py"

    context.log.info(f"Running YOLO enrichment: {script_path}")
    context.log.info(f"YOLO logs -> {log_file}")

    # Force UTF-8 environment for Windows and Progress Bars
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    with open(log_file, "a", encoding="utf-8") as f:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding="utf-8",  # Fixes UnicodeDecodeError: 'charmap'
            errors="replace",   # Prevents crash if a truly invalid char appears
            env=env,
        )

        # Stream output in real-time
        for line in process.stdout:
            print(line, end="", flush=True)
            f.write(line)

        process.wait()

        if process.returncode != 0:
            context.log.error(
                f"YOLO enrichment exited with code {process.returncode}")
            raise subprocess.CalledProcessError(
                process.returncode, process.args)

    context.log.info("YOLO enrichment completed successfully")


# -------------------------------------------------------
# LOAD YOLO RESULTS TO POSTGRES
# -------------------------------------------------------
@op(ins={"start": In(Nothing)})
def yolo_load_to_postgres(context: OpExecutionContext):
    """
    Load YOLO detection results from CSV into PostgreSQL.
    """
    log_file = logs_dir / "yolo_load_to_db.log"
    script_path = root / "src/medi_tg_analytics/loading/yolo_csv_to_db.py"
    

    context.log.info(f"Running YOLO result loader: {script_path}")
    context.log.info(f"YOLO Loader logs -> {log_file}")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    with open(log_file, "a", encoding="utf-8") as f:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding="utf-8",  # Consistency for Windows logs
            errors="replace",
            env=env,
        )

        for line in process.stdout:
            print(line, end="", flush=True)
            f.write(line)

        process.wait()

        if process.returncode != 0:
            context.log.error(
                f"YOLO Loader exited with code {process.returncode}")
            raise subprocess.CalledProcessError(
                process.returncode, process.args)

    context.log.info(
        "YOLO detection results loaded into PostgreSQL successfully")
