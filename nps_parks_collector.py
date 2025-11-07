"""
National Parks Data Collector for Google Colab
This script collects data from the National Park Service API and saves it to Google Sheets.

HOW TO USE:
1. Open this file in Google Colab
2. Paste your NPS API key in the API_KEY variable below
3. Paste your Google Sheet URL in the SHEET_URL variable below
4. Run all cells (Runtime > Run all)
"""

# ====================================================================
# IMPORTS
# ====================================================================
import requests
import pandas as pd
import gspread
from google.colab import auth
from google.auth import default

# ====================================================================
# CONFIGURATION - PASTE YOUR VALUES HERE
# ====================================================================

# PASTE YOUR NPS API KEY HERE (get one from: https://www.nps.gov/subjects/developer/get-started.htm)
API_KEY = "i0XgtcOuctDbL6U5IvI6vheVpXqIgtgq1CRGHKrF"

# PASTE YOUR GOOGLE SHEET URL HERE (make sure you have edit access)
SHEET_URL = "https://docs.google.com/spreadsheets/d/16S28nGRGDN7iCK12VHbKYfNkfh-4lJJjbi2ijCpHyAs/edit?usp=sharing"

# ====================================================================
# AUTHENTICATION
# ====================================================================

print("Authenticating with Google...")
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)
print("✓ Google authentication successful\n")

# ====================================================================
# FETCH DATA FROM NPS API
# ====================================================================

print("Fetching National Parks data from NPS API...")

# API endpoint
NPS_API_URL = "https://developer.nps.gov/api/v1/parks"

# Request parameters (limit to 50 parks)
params = {
    "api_key": API_KEY,
    "limit": 50
}

# Make API request
try:
    response = requests.get(NPS_API_URL, params=params)
    response.raise_for_status()  # Raise exception for bad status codes
    print(f"✓ API request successful (Status: {response.status_code})\n")
except requests.exceptions.RequestException as e:
    print(f"✗ Error making API request: {e}")
    raise

# Parse JSON response
try:
    data = response.json()
    parks_data = data.get("data", [])
    print(f"✓ Found {len(parks_data)} parks\n")
except ValueError as e:
    print(f"✗ Error parsing JSON response: {e}")
    raise

# ====================================================================
# EXTRACT AND PROCESS DATA
# ====================================================================

print("Processing park data...")

# Extract relevant fields for each park
parks_list = []
for park in parks_data:
    park_info = {
        "fullName": park.get("fullName", "N/A"),
        "states": park.get("states", "N/A"),
        "description": park.get("description", "N/A"),
        "acres": park.get("acres", "N/A"),
        "designation": park.get("designation", "N/A")
    }
    parks_list.append(park_info)

# Create pandas DataFrame
df = pd.DataFrame(parks_list)
print(f"✓ Created DataFrame with {len(df)} rows and {len(df.columns)} columns\n")
print("Preview of data:")
print(df.head())
print()

# ====================================================================
# WRITE TO GOOGLE SHEETS
# ====================================================================

print("Writing data to Google Sheets...")

try:
    # Open the Google Sheet
    sheet = gc.open_by_url(SHEET_URL)

    # Get the first worksheet (or create one if it doesn't exist)
    try:
        worksheet = sheet.get_worksheet(0)
    except:
        worksheet = sheet.add_worksheet(title="National Parks Data", rows=100, cols=10)

    # Clear existing data
    worksheet.clear()

    # Write data to sheet (including headers)
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    print(f"✓ Successfully wrote {len(df)} parks to Google Sheet!")
    print(f"✓ Sheet URL: {SHEET_URL}")

except gspread.exceptions.SpreadsheetNotFound:
    print("✗ Error: Could not find the Google Sheet. Make sure the URL is correct.")
    raise
except gspread.exceptions.APIError as e:
    print(f"✗ Google Sheets API error: {e}")
    raise
except Exception as e:
    print(f"✗ Unexpected error writing to Google Sheets: {e}")
    raise

# ====================================================================
# SUMMARY
# ====================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Parks collected: {len(df)}")
print(f"Fields extracted: {', '.join(df.columns)}")
print(f"Data written to: {SHEET_URL}")
print("="*60)
