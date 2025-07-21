#!/usr/bin/env python3

import pandas as pd
import sys

def filter_geotargets(csv_file, search_string):
    """
    Filter geotargets CSV by checking if Criteria ID or Parent ID contains the search string.
    
    Args:
        csv_file (str): Path to the CSV file
        search_string (str): String to search for in Criteria ID or Parent ID
    
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    df = pd.read_csv(csv_file)
    
    # Convert Criteria ID and Parent ID to strings for string matching
    criteria_matches = df['Criteria ID'].astype(str).str.contains(search_string, na=False)
    parent_matches = df['Parent ID'].astype(str).str.contains(search_string, na=False)
    
    # Filter rows where either Criteria ID or Parent ID contains the search string
    filtered_df = df[criteria_matches | parent_matches]
    
    return filtered_df

def main():
    csv_file = "geotargets-2025-07-15.csv"
    
    if len(sys.argv) > 1:
        search_string = sys.argv[1]
    else:
        search_string = input("Enter the number to search for: ")
    
    try:
        result = filter_geotargets(csv_file, search_string)
        
        if len(result) > 0:
            print(f"\nFound {len(result)} matching records:")
            
            # Convert to long format: each variable becomes a row
            for idx, row in result.iterrows():
                print(f"\n--- Record {idx + 1} ---")
                for column, value in row.items():
                    print(f"{column:<15}: {value}")
        else:
            print(f"\nNo records found containing '{search_string}' in Criteria ID or Parent ID")
            
    except FileNotFoundError:
        print(f"Error: {csv_file} not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()