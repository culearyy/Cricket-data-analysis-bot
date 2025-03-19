import requests
import pandas as pd

# URL containing the cricket data
url = ("https://stats.espncricinfo.com/ci/engine/stats/index.html?"
       "class=2;home_or_away=1;home_or_away=2;home_or_away=3;"
       "spanmin1=1+Jan+2020;spanval1=span;team=6;template=results;type=batting")

# Define headers to mimic a web browser
headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/115.0 Safari/537.36")
}

# Fetch the webpage using the custom headers
response = requests.get(url, headers=headers)

# Check if the response status is OK (200)
try:
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(f"HTTP error occurred: {e}")
    exit(1)

# Optionally, you can check the status code
if response.status_code != 200:
    print(f"Unexpected status code: {response.status_code}")
    exit(1)

# Use pandas to read all tables in the page
try:
    tables = pd.read_html(response.text)
except ValueError as ve:
    print("No tables found in the HTML. The page structure may have changed or the data may be loaded dynamically.")
    exit(1)

# Check if any tables were found
if not tables:
    print("No tables found on the page.")
    exit(1)

# For this example, assume the main data table is the first one
df = tables[0]

# Optionally, print out the first few rows to verify the data
print(df.head())

# Save the DataFrame to a CSV file
csv_filename = "cricket_data.csv"
df.to_csv(csv_filename, index=False)
print(f"Data has been saved to '{csv_filename}'")
