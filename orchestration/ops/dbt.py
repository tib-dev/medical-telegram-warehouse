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
# RUN DBT TRANSFORMATIONS
# -------------------------------------------------------
@op(ins={"start": In(Nothing)})
def run_dbt_transformations(context: OpExecutionContext):
    """
    Execute dbt transformations on the raw data.
    """
    log_file = logs_dir / "dbt_transformations.log"
    # Ensure script path is handled correctly across OS
    script_path = root / "scripts" / "run_dbt.py"

    context.log.info(f"Running dbt transformations: {script_path}")
    context.log.info(f"dbt logs -> {log_file}")

    # 1. Fix Environment for Windows/UTF-8
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    # Optional: forces dbt to not use 'pretty' colors if you still see issues
    # env["DBT_PREREQUISITES_COLOR"] = "false"

    # 2. Use utf-8 encoding for the log file
    with open(log_file, "a", encoding="utf-8") as f:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=env,
        )

        # Stream output in real-time
        for line in process.stdout:
            # flush=True helps output appear in Dagster UI immediately
            print(line, end="", flush=True)
            f.write(line)

        process.wait()

        if process.returncode != 0:
            context.log.error(
                f"dbt transformations exited with code {process.returncode}"
            )
            raise subprocess.CalledProcessError(
                process.returncode, process.args
            )

    context.log.info("dbt transformations completed successfully")
