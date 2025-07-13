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
OUTPUT_FILE = 'data/raw_data.csv'
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
            - Dimensions: date, country, city
            - Metrics: activeUsers, newUsers
            - Date range: from 2020-04-01 to 2030-12-31
    """
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
    """Process the GA response into a pandas DataFrame.
    
    Args:
        response: Google Analytics API response object
        
    Returns:
        pd.DataFrame: Processed DataFrame with:
            - Columns: date, country, city, activeUsers, newUsers
            - Sorted by date
            - Numeric metrics
            - Properly formatted datetime
    """
    data = []
    for row in tqdm(response.rows, desc="Processing rows"):
        dimension_values = [value.value for value in row.dimension_values]
        metric_values = [value.value for value in row.metric_values]
        data.append(dimension_values + metric_values)

    columns = [dim.name for dim in response.dimension_headers] + [metric.name for metric in response.metric_headers]
    df = pd.DataFrame(data, columns=columns)
    
    # Data cleaning - keep date as string to match archive format
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    df = df.sort_values('date')
    
    # Convert metrics to numeric, then back to int to match archive format
    df['activeUsers'] = pd.to_numeric(df['activeUsers']).astype(int)
    df['newUsers'] = pd.to_numeric(df['newUsers']).astype(int)
    
    # Replace "(not set)" with ""
    df = df.replace("(not set)", "")
    
    return df

def load_existing_data(file_path: Path) -> pd.DataFrame:
    """Load existing data from CSV file if it exists.
    
    Args:
        file_path (Path): Path to the existing CSV file
        
    Returns:
        pd.DataFrame: Loaded DataFrame with date column as string to match format,
                     or empty DataFrame if file doesn't exist
    """
    if file_path.exists():
        df = pd.read_csv(file_path)
        # Keep date as string to match archive format - no conversion needed
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
        - Removes duplicates based on date, country, and city
        - Keeps the most recent version of duplicate entries
        - Sorts final data by date
        - Creates output directory if it doesn't exist
    """
    try:
        if existing_df.empty:
            final_df = new_df
            logging.info("No existing data found!")
        
        else:
            # Combine existing and new data
            combined_df = pd.concat([existing_df, new_df])
            
            # Replace NaN with ""
            combined_df = combined_df.fillna("")
            
            # Replace "(not set)" with "" in combined data (both new and existing)
            combined_df = combined_df.replace("(not set)", "")
            
            # Remove duplicates based on date, country, and city
            final_df = combined_df.drop_duplicates(subset=['date', 'country', 'city'], keep='last')
            
            # Sort by date
            final_df = final_df.sort_values('date')
        
        # Apply final cleaning to ensure no "(not set)" values remain
        final_df = final_df.replace("(not set)", "")
        
        # Ensure the output path is absolute
        output_path = output_path.resolve()
        
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
        for file in archive_dir.glob('raw_data_*.csv'):
            match = archive_pattern.match(file.name)
            if match:
                date_str = match.group(1)
                archive_date = datetime.strptime(date_str, '%Y-%m-%d')
                archive_files.append((file, archive_date))
        
        # Sort by date (newest first)
        archive_files.sort(key=lambda x: x[1], reverse=True)

        # If archive_files is empty, create a new archive
        if not archive_files:
            archive_filename = f"raw_data_{today.strftime('%Y-%m-%d')}.csv"
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
            archive_filename = f"raw_data_{today.strftime('%Y-%m-%d')}.csv"
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
        1. Load existing data from CSV
        2. Initialize GA client
        3. Create and execute report request
        4. Process response into DataFrame
        5. Merge with existing data
        6. Save results
        7. Archive data if needed
    
    Raises:
        Exception: If any step fails
    """
    try:
        dirname = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
        credentials_path = dirname / CREDENTIALS_PATH
        output_path = dirname / OUTPUT_FILE
        ga_id = GA_ID

        # Validate credentials file exists
        if not credentials_path.exists():
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

        # Load existing data
        existing_df = load_existing_data(output_path)
        
        # Setup client and create request
        client = setup_ga_client(str(credentials_path))
        request = create_report_request(ga_id)
        
        # Execute request and process response
        logging.info("Executing Google Analytics request...")
        response = client.run_report(request)
        
        # Validate response
        if not hasattr(response, 'rows') or len(response.rows) == 0:
            logging.warning("No data returned from Google Analytics")
            return
        
        new_df = process_response(response)
        logging.info(f"Processed {len(new_df)} rows of new data")
        
        # Merge and save results
        merge_and_save_data(new_df, existing_df, output_path)
        
        # Check if we need to archive the data
        check_and_archive_data(dirname, OUTPUT_FILE)
        
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()