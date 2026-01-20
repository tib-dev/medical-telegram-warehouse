from dagster import job
from orchestration.ops.scrape import scrape_telegram_data
from orchestration.ops.load import load_raw_to_postgres
from orchestration.ops.dbt import run_dbt_transformations
from orchestration.ops.yolo import run_yolo_enrichment, yolo_load_to_postgres  


@job
def medical_telegram_pipeline():
    # 1. Scrape both images and JSON
    scrape = scrape_telegram_data()

    # 2. Parallel Loading Paths
    # Load the raw message JSONs
    load_msgs = load_raw_to_postgres(start=scrape)

    # Run YOLO inference on images and then load the resulting CSV
    yolo_csv = run_yolo_enrichment(start=scrape)
    load_yolo = yolo_load_to_postgres(start=yolo_csv)

    # 3. Transformation (dbt)
    # dbt now waits for BOTH loaders to finish so all 'raw' tables are ready
    transform = run_dbt_transformations(start=[load_msgs, load_yolo])
