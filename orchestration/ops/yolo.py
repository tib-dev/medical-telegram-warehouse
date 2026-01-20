from dagster import op
import subprocess


@op
def run_yolo_enrichment():
    subprocess.run(
        ["bash", "scripts/run_yolo.sh"],
        check=True
    )
