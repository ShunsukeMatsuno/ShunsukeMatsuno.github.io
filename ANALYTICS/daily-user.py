from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, MetricType
)
import pandas as pd
import os
import sys
import logging
from typing import List, Dict
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_ga_client(credentials_path: str) -> BetaAnalyticsDataClient:
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        return BetaAnalyticsDataClient()
    except Exception as e:
        logging.error(f"Failed to initialize GA client: {e}")
        raise

def create_report_request(ga_id: str) -> RunReportRequest:
    return RunReportRequest(
        property=f"properties/{ga_id}",
        dimensions=[
            Dimension(name="date"),
            Dimension(name="country"),
            Dimension(name="city")
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="newUsers")
        ],
        date_ranges=[DateRange(start_date="2020-04-01", end_date="2030-12-31")],
    )

def process_response(response) -> pd.DataFrame:
    data = []
    for row in tqdm(response.rows, desc="Processing rows"):
        dimension_values = [value.value for value in row.dimension_values]
        metric_values = [value.value for value in row.metric_values]
        data.append(dimension_values + metric_values)

    columns = [dim.name for dim in response.dimension_headers] + [metric.name for metric in response.metric_headers]
    df = pd.DataFrame(data, columns=columns)
    
    # Data cleaning
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Convert metrics to numeric
    df['activeUsers'] = pd.to_numeric(df['activeUsers'])
    df['newUsers'] = pd.to_numeric(df['newUsers'])
    
    return df

def load_existing_data(file_path: Path) -> pd.DataFrame:
    if file_path.exists():
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()

def merge_and_save_data(new_df: pd.DataFrame, existing_df: pd.DataFrame, output_path: Path) -> None:
    try:
        if existing_df.empty:
            final_df = new_df
        else:
            # Combine existing and new data
            combined_df = pd.concat([existing_df, new_df])
            
            # Remove duplicates based on date, country, and city
            final_df = combined_df.drop_duplicates(subset=['date', 'country', 'city'], keep='last')
            
            # Sort by date
            final_df = final_df.sort_values('date')
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(output_path, index=False)
        logging.info(f"Data saved successfully to {output_path}")
        
        # Log summary of changes
        if not existing_df.empty:
            new_rows = len(final_df) - len(existing_df)
            logging.info(f"Added {new_rows} new rows to the dataset")
            
    except Exception as e:
        logging.error(f"Failed to save data: {e}")
        raise

def main():
    try:
        dirname = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
        credentials_path = dirname / "my-website-analytics-b37a5d44bcc6.json"
        output_path = dirname / "data/raw_data.csv"
        ga_id = '434705894'

        # Load existing data
        existing_df = load_existing_data(output_path)
        
        client = setup_ga_client(str(credentials_path))
        request = create_report_request(ga_id)
        
        logging.info("Fetching GA4 data...")
        response = client.run_report(request)
        
        new_df = process_response(response)
        merge_and_save_data(new_df, existing_df, output_path)
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()