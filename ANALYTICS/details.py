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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration
CREDENTIALS_PATH = "my-website-analytics-b37a5d44bcc6.json"
GA_ID = '434705894'
OUTPUT_FILE = 'data/raw_data_detail.csv'

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
        row['deviceCategory'] if row['deviceModel'] == "(not set)" else
        f"{row['deviceCategory']} ({row['deviceModel']})",
        axis=1
    )

    # Drop deviceCategory and deviceModel columns
    df = df.drop(columns=['deviceCategory', 'deviceModel'])
    
    # Convert newUsers=1 to "New" and newUsers=0 to ""
    df['newUsers'] = df['newUsers'].apply(lambda x: "New" if x == "1" else "")

    # Sort by time
    df = df.sort_values('time')

    # Delete data in linkUrl column if it is in my website
    df = df[~df['linkUrl'].str.contains('shunsukematsuno.github.io')]

    # Replace "(not set)" with ""
    df = df.replace("(not set)", "")
    return df

    # Order columns
    df = df[['time', 'country', 'city', 'device', 'page', 'fileName', 'linkUrl', 'newUsers']]
    return df

def load_existing_data(file_path: Path) -> pd.DataFrame:
    """Load existing data from CSV file if it exists.
    
    Args:
        file_path (Path): Path to the existing CSV file
        
    Returns:
        pd.DataFrame: Loaded DataFrame with time column converted to datetime,
            or empty DataFrame if file doesn't exist
    """
    if file_path.exists():
        df = pd.read_csv(file_path)
        df['time'] = pd.to_datetime(df['time'])
        return df
    return pd.DataFrame()

def merge_and_save_data(new_df: pd.DataFrame, existing_df: pd.DataFrame, output_path: Path) -> None:
    """Merge new data with existing data and save to CSV.
    
    Args:
        new_df (pd.DataFrame): New data from GA
        existing_df (pd.DataFrame): Existing data from CSV
        output_path (Path): Path where to save the merged data
        
    Raises:
        Exception: If saving fails
        
    Note:
        - Removes duplicates based on all columns
        - Keeps the most recent version of duplicate entries
        - Sorts final data by time
        - Creates output directory if it doesn't exist
    """
    try:
        if existing_df.empty:
            final_df = new_df
        else:
            # Combine existing and new data
            combined_df = pd.concat([existing_df, new_df])
            
            # Remove duplicates based on all columns
            final_df = combined_df.drop_duplicates(
                subset=combined_df.columns.tolist(),
                keep='last'
            )
            
            # Sort by time
            final_df = final_df.sort_values('time')

            # Drop activeUsers column
            final_df = final_df.drop(columns=['activeUsers'])
        
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
    """Main function to run the GA data extraction process.
    
    Workflow:
        1. Initialize GA client
        2. Create and execute report request
        3. Process response into DataFrame
        4. Load existing data from CSV
        5. Merge with existing data
        6. Save results
    
    Raises:
        Exception: If any step fails
    """
    try:
        # Setup client
        client = setup_ga_client(CREDENTIALS_PATH)
        
        # Create and execute request
        request = create_report_request(GA_ID)
        logging.info("Executing Google Analytics request...")
        response = client.run_report(request)
        
        # Process response
        new_df = process_response(response)
        logging.info(f"Processed {len(new_df)} rows of new data")
        
        # Load existing data and merge
        dirname = Path(os.path.dirname(os.path.abspath(__file__)))
        output_path = dirname / OUTPUT_FILE
        existing_df = load_existing_data(output_path)
        
        # Merge and save results
        merge_and_save_data(new_df, existing_df, output_path)
        
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()