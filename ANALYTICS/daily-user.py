from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    MetricType
)

import pandas as pd
import os
import sys

dirname = os.path.dirname(os.path.abspath(sys.argv[0]))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(dirname, "ANALYTICS/my-website-analytics-b37a5d44bcc6.json")
GAid = '434705894'

client = BetaAnalyticsDataClient()
request = RunReportRequest(
    property=f"properties/{GAid}",
    dimensions=[
        Dimension(name="date"),
        Dimension(name="country"),
        Dimension(name="city")
    ],
    metrics=[
        Metric(name="activeUsers"),
        Metric(name="newUsers")
    ],
    # date_ranges=[DateRange(start_date="2020-04-01", end_date="today")],
    date_ranges=[DateRange(start_date="2020-04-01", end_date="2030-12-31")],
)

# Execute GA4 request
response = client.run_report(request)

# Extract GA4 data into pandas DataFrame
data = []
for row in response.rows:
    dimension_values = [value.value for value in row.dimension_values]
    metric_values = [value.value for value in row.metric_values]
    data.append(dimension_values + metric_values)

columns = [dimension.name for dimension in response.dimension_headers] + [metric.name for metric in response.metric_headers]
df = pd.DataFrame(data, columns=columns)

# Sort by date
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Get the last 20 rows (recent access)
df_recent = df.tail(20)

filename = os.path.join(dirname, 'data/raw_data.csv')
try:
    df.to_csv(filename, index=False)
    print(f"CSV file has been written successfully: {filename}")
except Exception as e:
    print(f"An error occurred while writing the CSV file: {e}")
