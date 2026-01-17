# Medical Telegram Analytics

**Shipping a Data Product: From Raw Telegram Data to an Analytical API**  
An end-to-end data pipeline for Telegram, leveraging dbt for transformations, Dagster for orchestration, and YOLOv8 for image enrichment.

This project extracts, transforms, enriches, and serves Telegram messages related to Ethiopian medical and pharmaceutical products, providing actionable analytics via an API.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Business Context](#business-context)
- [Objectives](#objectives)
- [Data & Features](#data--features)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Pipeline & Processing Steps](#pipeline--processing-steps)
- [Engineering Practices](#engineering-practices)
- [Setup & Installation](#setup--installation)
- [Running the Project](#running-the-project)
- [Technologies Used](#technologies-used)
- [Author](#author)

---

## Project Overview

This project implements a **Telegram analytics pipeline** for Ethiopian medical businesses.  
It handles the full ELT lifecycle:

- Scraping messages and images from public Telegram channels
- Loading raw data into a data lake and PostgreSQL warehouse
- Transforming data into a dimensional star schema with dbt
- Enriching data using YOLOv8 object detection
- Exposing actionable insights through a FastAPI analytical API

---

## Business Context

Kara Solutions, a leading data consultancy in Ethiopia, requires a **scalable and reliable data platform** to track products, pricing, and visual content trends across Telegram channels.

Key business questions addressed:

1. Top 10 most frequently mentioned medical products or drugs
2. Price or availability variation of a product across channels
3. Channels with the most visual content (e.g., images of pills vs. creams)
4. Daily and weekly trends in posting volume for health-related topics

---

## Objectives

- Build a reproducible and secure data pipeline environment
- Extract Telegram messages and media into a raw data lake
- Design and implement a dimensional star schema in PostgreSQL
- Transform raw data using dbt, ensuring cleanliness and consistency
- Enrich images with YOLOv8 for object detection
- Serve final data through a FastAPI analytical API
- Orchestrate the full pipeline with Dagster
- Ensure reproducibility and versioning with DVC

---

## Data & Features

**Telegram Channels Scraped:**

- CheMed Telegram Channel – Medical products
- Lobelia Cosmetics – Cosmetics & health products
- Tikvah Pharma – Pharmaceuticals
- Additional channels from [et.tgstat.com/medicine](https://et.tgstat.com/medicine)

**Data Fields Collected:**

| Column       | Description                        |
| ------------ | ---------------------------------- |
| message_id   | Unique message identifier          |
| channel_name | Telegram channel name              |
| message_date | Timestamp of message               |
| message_text | Full text content                  |
| has_media    | Whether the message contains media |
| image_path   | Path to downloaded image           |
| views        | Number of views                    |
| forwards     | Number of forwards                 |

**Derived Features:**

- Message length and content flags
- YOLOv8-based image categories (promotional, product_display, lifestyle, other)
- Aggregated metrics per channel and time period

---

## Project Structure

```text
medical-telegram-analytics/
│
├── config/                      # YAML configs: DB, API, YOLO, pipeline
├── data/                        # Raw, interim, processed datasets
│   ├── raw/telegram_messages/
│   └── raw/images/
├── logs/                        # Logs for scraping, enrichment, API, Dagster
├── notebooks/                    # EDA, testing, analysis
├── scripts/                      # CLI scripts for scraper, dbt, API, pipeline
├── src/
│   └── tg_warehouse/            # Python package
│       ├── scraping/            # Telegram scraping logic
│       ├── loading/             # Load raw → warehouse
│       └── enrichment/          # YOLOv8 image analysis
├── api/                          # FastAPI analytical API
│   └── routers/                 # API endpoints: reports, search, channels
├── dbt/                          # dbt project
│   └── medical_warehouse/
│       ├── models/staging/
│       ├── models/marts/
│       └── tests/
├── orchestration/                # Dagster pipeline definition
├── tests/                        # Unit & integration tests
├── docker/                       # Dockerfile and docker-compose
├── dvc.yaml                       # DVC pipeline for reproducibility
├── params.yaml                    # Global pipeline parameters
├── requirements.txt
├── .env                           # Environment variables
└── README.md
```

---

## Architecture

```text
Telegram Channels
      │
      ▼
 Scraper (src/scraping)
      │
      ▼
 Raw Data → Data Lake (JSON + Images)
      │
      ▼
 PostgreSQL Raw Schema → dbt Staging → dbt Marts (Dimensional Star Schema)
      │
      ▼
 Enrichment (YOLOv8 Image Detection)
      │
      ▼
 FastAPI Analytical API
      │
      ▼
 Users / Dashboards / Reports
```

---

## Pipeline & Processing Steps

1. **Data Scraping (Extract & Load)**

   - Telethon extracts messages and media
   - Raw JSON saved by channel/date in `data/raw/telegram_messages`
   - Images downloaded to `data/raw/images/{channel_name}/{message_id}.jpg`

2. **Data Warehouse (Transform)**

   - Raw JSON loaded to PostgreSQL (`raw.telegram_messages`)
   - dbt staging models clean, normalize, and cast data types
   - Dimensional star schema with: `dim_channels`, `dim_dates`, `fct_messages`, `fct_image_detections`

3. **Data Enrichment**

   - YOLOv8 detects objects in images
   - Categorizes images (promotional, product_display, lifestyle, other)
   - Results joined to `fct_messages` for enriched analytics

4. **Analytical API**

   - FastAPI exposes endpoints:
     - `/api/reports/top-products`
     - `/api/channels/{channel_name}/activity`
     - `/api/search/messages`
     - `/api/reports/visual-content`
   - Pydantic schemas validate requests and responses

5. **Orchestration**
   - Dagster pipeline automates scraping, loading, transformations, enrichment
   - Scheduled daily with logging and error notifications

---

## Engineering Practices

- **Reproducibility:** DVC tracks datasets, dbt outputs, and YOLO results
- **Containerization:** Docker & docker-compose ensure consistent environments
- **Testing:** Unit and integration tests for scraping, dbt models, enrichment, API
- **Environment Management:** `.env.example` template, local `.env` ignored
- **Logging & Monitoring:** Per-stage logs stored in `logs/`

---

## Setup & Installation

```bash
git clone https://github.com/<username>/medical-telegram-analytics.git
cd medical-telegram-analytics

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Fill in database credentials, Telegram API keys, YOLO model path
```

---

## Running the Project

### Run full pipeline with DVC

```bash
dvc repro
```

### Run individual scripts

```bash
scripts/run_scraper.sh
scripts/run_dbt.sh
scripts/run_pipeline.sh
scripts/run_api.sh
```

### Access API

- FastAPI docs: `http://localhost:8000/docs`
- Example endpoints:
  - `/api/reports/top-products?limit=10`
  - `/api/channels/CheMed/activity`
  - `/api/search/messages?query=aspirin&limit=20`

---

## Technologies Used

- Python 3.10+
- PostgreSQL
- dbt for transformations
- YOLOv8 for image enrichment
- FastAPI for analytical endpoints
- Dagster for orchestration
- DVC for dataset and pipeline versioning
- Docker & docker-compose for reproducible environment
- Telethon for Telegram scraping
- Pytest for testing

---

## Author

Tibebu Kaleb – Full-stack AI/ML engineer experienced in data pipelines, NLP, RAG, CV, and analytical API development
