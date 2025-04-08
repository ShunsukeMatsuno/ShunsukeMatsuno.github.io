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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration
CREDENTIALS_PATH = "my-website-analytics-b37a5d44bcc6.json"
GA_ID = '434705894'
OUTPUT_FILE = 'data/raw_data_detail.csv'
ARCHIVE_DIR = 'data/archive' 

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

    # Drop deviceCategory and deviceModel columns
    df = df.drop(columns=['deviceCategory', 'deviceModel'])
    
    # Convert newUsers=1 to "New" and newUsers=0 to ""
    df['newUsers'] = df['newUsers'].apply(lambda x: "New" if x == "1" else "Return")

    # Sort by time
    df = df.sort_values('time')

    # Replace linkUrl with "" in linkUrl column if it is in my website
    df['linkUrl'] = df['linkUrl'].apply(lambda x: "" if "shunsukematsuno.github.io" in x else x)

    # Replace "(not set)" with ""
    df = df.replace("(not set)", "")

    # Order columns
    df = df[['time', 'country', 'city', 'device', 'newUsers', 'page', 'fileName', 'linkUrl']]
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
            logging.info("No existing data found!")
        else:
            # Combine existing and new data
            combined_df = pd.concat([existing_df, new_df])

            # Drop activeUsers column if it exists
            if 'activeUsers' in combined_df.columns:
                combined_df = combined_df.drop(columns=['activeUsers'])

            # Replace NaN with ""
            combined_df = combined_df.fillna("")

            # Remove duplicates based on all columns
            final_df = combined_df.drop_duplicates()
            
            # Sort by time
            final_df = final_df.sort_values('time')
            
        # Ensure the output path is absolute
        output_path = output_path.resolve()
        
        # Save to file
        final_df.to_csv(output_path, index=False)
        logging.info(f"Data saved successfully to {output_path}")

        # Log summary of changes
        if not existing_df.empty:
            new_rows = len(final_df) - len(existing_df)
            logging.info(f"Added {new_rows} new rows to the dataset")
            
    except Exception as e:
        logging.error(f"Failed to save data: {e}")
        raise

def check_and_archive_data(dirname: Path, output_file: str) -> None:
    """Check if we need to archive the current data file.
    
    Args:
        dirname (Path): Directory where the script is located
        output_file (str): Path to the current data file
        
    Note:
        - Creates archive directory if it doesn't exist
        - Archives data if the latest archive is at least a month old
        - Names the archive with today's date
    """
    try:
        today = datetime.now()
        archive_dir = dirname / ARCHIVE_DIR
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract the base filename without extension from OUTPUT_FILE
        base_filename = Path(OUTPUT_FILE).stem
        archive_pattern = re.compile(rf'{base_filename}_(\d{{4}}-\d{{2}}-\d{{2}})\.csv')
        archive_files = []
        
        # Get all archived files
        for file in archive_dir.glob('raw_data_detail_*.csv'):
            match = archive_pattern.match(file.name)
            if match:
                date_str = match.group(1)
                archive_date = datetime.strptime(date_str, '%Y-%m-%d')
                archive_files.append((file, archive_date))
        
        # Sort by date (newest first)
        archive_files.sort(key=lambda x: x[1], reverse=True)

        # If archive_files is empty, create a new archive
        if not archive_files:
            archive_filename = f"raw_data_detail_{today.strftime('%Y-%m-%d')}.csv"
            archive_path = archive_dir / archive_filename
            shutil.copy2(dirname / OUTPUT_FILE, archive_path)
            logging.info(f"Archived current data to {archive_path}")
            return
        
        # Check if we need to archive
        should_archive = True
        logging.info(f"archive_files: {archive_files[0][0]}")
        if archive_files:
            latest_archive_date = archive_files[0][1]
            # If the latest archive is less than a month old, don't archive
            if (today - latest_archive_date).days < 30:
                should_archive = False
                logging.info(f"Latest archive is from {latest_archive_date.date()}, less than a month ago. Skipping archiving.")
        
        if should_archive:
            # Create new archive file
            archive_filename = f"raw_data_detail_{today.strftime('%Y-%m-%d')}.csv"
            archive_path = archive_dir / archive_filename
            
            # Ensure source file exists and is absolute
            source_file = (dirname / output_file).resolve()
            if not source_file.exists():
                logging.error(f"Source file {source_file} does not exist")
                return
                
            # Copy current data to archive
            shutil.copy2(source_file, archive_path)
            logging.info(f"Archived current data to {archive_path}")
    
    except Exception as e:
        logging.error(f"Failed to archive data: {e}")
        # Don't raise the exception to allow the main process to continue

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
        
        # Check if we need to archive the data
        check_and_archive_data(dirname, OUTPUT_FILE)
        
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
