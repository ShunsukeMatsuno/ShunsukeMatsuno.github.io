from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest
)
import pandas as pd
import os
import logging
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict
from datetime import datetime, timedelta
import re
import shutil

# Configuration
CREDENTIALS_PATH = "my-website-analytics-b37a5d44bcc6.json"
GA_ID = '434705894'

def setup_ga_client(credentials_path: str) -> BetaAnalyticsDataClient:
    """Initialize the Google Analytics client with credentials.
    
    Args:
        credentials_path (str): Path to the Google Analytics credentials JSON file
        
    Returns:
        BetaAnalyticsDataClient: Initialized GA client
        
    Raises:
        Exception: If client initialization fails
    """
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        return BetaAnalyticsDataClient()
    except Exception as e:
        logging.error(f"Failed to initialize GA client: {e}")
        raise

def create_report_request(ga_id: str) -> RunReportRequest:
    """Create a report request with specified dimensions and metrics.
    
    Args:
        ga_id (str): Google Analytics property ID
        
    Returns:
        RunReportRequest: Configured request object with:
            - Dimensions: dateHourMinute, country, city, deviceCategory, deviceModel, pagePathPlusQueryString, fileName, linkUrl
            - Metrics: activeUsers, newUsers
            - Date range: from 2020-04-01 to today
    """
    return RunReportRequest(
        property=f"properties/{ga_id}",
        dimensions=[
            Dimension(name="dateHourMinute"),
            Dimension(name="country"),
            Dimension(name="city"),
            Dimension(name="deviceCategory"),
            Dimension(name="deviceModel"),
            Dimension(name="pagePathPlusQueryString"),
            Dimension(name="fileName"),
            Dimension(name="linkUrl")
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="newUsers")
        ],
        date_ranges=[DateRange(start_date="2020-04-01", end_date="today")],
    )

def process_response(response) -> pd.DataFrame:
    """Process the GA response into a pandas DataFrame.
    
    Args:
        response: Google Analytics API response object
        
    Returns:
        pd.DataFrame: Processed DataFrame with:
            - Columns: time, country, city, device, page, fileName, linkUrl, newUsers
            - Sorted by time
            - Numeric metrics
            - Properly formatted datetime (YYYYMMDDHHMM format)
    """
    data = []
    for row in tqdm(response.rows, desc="Processing rows"):
        dimension_values = [value.value for value in row.dimension_values]
        metric_values = [value.value for value in row.metric_values]
        data.append(dimension_values + metric_values)

    columns = [dim.name for dim in response.dimension_headers] + [metric.name for metric in response.metric_headers]
    df = pd.DataFrame(data, columns=columns)
    
    # Rename columns
    df = df.rename(columns={'pagePathPlusQueryString': 'page',
                            'dateHourMinute': 'time'})
    
    # Format dateHourMinute (YYYYMMDDHHMM)
    df['time'] = pd.to_datetime(df['time'].astype(str), format="%Y%m%d%H%M")
    
    # Create device column combining deviceCategory and deviceModel
    df['device'] = df.apply(
        lambda row: 
        "(not set)" if row['deviceCategory'] == "(not set)" and row['deviceModel'] == "(not set)" else
        row['deviceCategory'] if row['deviceModel'] == "(not set)" or row['deviceModel'] == "" else
        f"{row['deviceCategory']} ({row['deviceModel']})",
        axis=1
    )

    # Convert newUsers=1 to "New" and newUsers=0 to ""
    df['newUsers'] = df['newUsers'].apply(lambda x: "New" if x == "1" else "Return")

    # Sort by time
    df = df.sort_values('time')

    # Replace linkUrl with "" in linkUrl column if it is in my website
    df['linkUrl'] = df['linkUrl'].apply(lambda x: "" if "shunsukematsuno.github.io" in x else x)

    # Replace "(not set)" with ""
    df = df.replace("(not set)", "")

    # Order columns
    # df = df[['time', 'country', 'city', 'device', 'newUsers', 'page', 'fileName', 'linkUrl']]
    return df


def main():
    """Main function to run the GA data extraction process.
    
    Workflow:
        1. Initialize GA client
        2. Create and execute report request
        3. Process response into DataFrame
        4. Load existing data from CSV
        5. Merge with existing data
        6. Save results
        7. Archive data if needed
    
    Raises:
        Exception: If any step fails
    """
    # Setup client
    client = setup_ga_client(CREDENTIALS_PATH)
    
    # Create and execute request
    request = create_report_request(GA_ID)
    logging.info("Executing Google Analytics request...")
    response = client.run_report(request)
    
    # Process response
    df = process_response(response)

    # Save to csv
    df.to_csv('test.csv', index=False)

if __name__ == "__main__":
    main()