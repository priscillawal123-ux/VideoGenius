#!/usr/bin/env python3
"""
Setup script for BigQuery dataset and tables.
"""

import os

from google.cloud import bigquery

# Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/walland/credentials.json"


def setup_bigquery():
    """Setup BigQuery dataset and tables for Video Genius."""

    project_id = "video-genius-prod-v1"
    dataset_id = "video_data"

    client = bigquery.Client(project=project_id)

    # Create dataset
    dataset_ref = client.dataset(dataset_id)

    try:
        dataset = client.get_dataset(dataset_ref)
        print(f"✅ Dataset {dataset_id} already exists")
    except Exception:
        print(f"📦 Creating dataset {dataset_id}...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset)
        print(f"✅ Dataset {dataset_id} created successfully")

    # Create video_jobs table
    table_id = "video_jobs"
    table_ref = dataset_ref.table(table_id)

    schema = [
        bigquery.SchemaField("job_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("topic", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("duration_seconds", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("style", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("script", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("video_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("error_message", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("progress_percentage", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("estimated_completion_time", "INTEGER", mode="NULLABLE"),
    ]

    try:
        table = client.get_table(table_ref)
        print(f"✅ Table {table_id} already exists")
    except Exception:
        print(f"📋 Creating table {table_id}...")

        table = bigquery.Table(table_ref, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY, field="created_at"
        )

        table = client.create_table(table)
        print(f"✅ Table {table_id} created successfully")

    print("\n🎉 BigQuery setup completed!")
    print(f"   Project: {project_id}")
    print(f"   Dataset: {dataset_id}")
    print(f"   Table: {table_id}")


if __name__ == "__main__":
    setup_bigquery()
