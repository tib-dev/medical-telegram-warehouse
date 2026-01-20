#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

from medi_tg_analytics.core.project_root import get_project_root


def run_cmd(cmd: list[str], cwd: Path) -> None:
    """Run a shell command in a given directory and fail fast on error."""
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f" Command failed: {' '.join(cmd)}")
        sys.exit(exc.returncode)


def load_env():
    """Load environment variables from .env file and validate required DB creds."""
    root = get_project_root()
    env_path = root / ".env"

    if not env_path.exists():
        print(f".env file not found at {env_path}")
        sys.exit(1)

    load_dotenv(dotenv_path=env_path)

    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
    missing = [v for v in required_vars if v not in os.environ]
    if missing:
        print(
            f" Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    print("✅ Environment variables loaded successfully")


def main():
    print("=" * 56)
    print("Running dbt models, tests, and generating docs")
    print("=" * 56)

    load_env()  # load DB credentials automatically

    # Resolve project root
    root = get_project_root()
    dbt_project_dir = root / "dbt" / "medical_warehouse"

    if not dbt_project_dir.exists():
        print(f" dbt project directory not found: {dbt_project_dir}")
        sys.exit(1)

    print(f"Using dbt project directory: {dbt_project_dir}")

    try:
        print("Cleaning dbt artifacts...")
        run_cmd(["dbt", "clean"], cwd=dbt_project_dir)

        print(" Running dbt models...")
        run_cmd(["dbt", "run"], cwd=dbt_project_dir)

        print(" Running dbt tests...")
        run_cmd(["dbt", "test"], cwd=dbt_project_dir)

    except KeyboardInterrupt:
        print("\n Execution interrupted by user")
        sys.exit(130)

    print("=" * 56)
    print("dbt pipeline completed successfully")
    print("=" * 56)


if __name__ == "__main__":
    main()
