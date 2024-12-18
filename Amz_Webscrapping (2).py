#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
from tqdm.notebook import tqdm
import urllib3

# Suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# In[2]:


class AmazonScraper:
    def __init__(self):
        # User-Agent list to rotate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
    
    def get_product_details(self, asin):
        """
        Scrape product details from Amazon for a given ASIN
        """
        url = f'https://www.amazon.in/dp/{asin}'
        
        try:
            # Random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            # Rotate User-Agent
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            # Send request
            response = requests.get(
                url, 
                headers=headers, 
                verify=False,  # Be cautious with this
                timeout=10
            )
            
            # Check if request was successful
            if response.status_code != 200:
                print(f"Failed to retrieve page for ASIN {asin}. Status code: {response.status_code}")
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Safe extraction function
            def safe_extract(selector, attribute='text', strip=True):
                try:
                    element = soup.select_one(selector)
                    if not element:
                        return 'N/A'
                    
                    if attribute == 'text':
                        return element.get_text(strip=strip)
                    else:
                        return element.get(attribute, 'N/A')
                except Exception:
                    return 'N/A'
            
            # Check for availability
            availability_text = safe_extract('#availability span')
            
            # Title extraction
            title = safe_extract('#productTitle')
            
            # Detailed availability check
            is_available = 'Currently Unavailable' not in availability_text
            
            # Price extraction with multiple scenarios
            price = 'N/A'
            if is_available:
                # Existing price extraction logic
                price_selectors = [
                    '.a-price .a-offscreen',
                    '.a-price-whole',
                    '.a-price-fraction'
                ]
                price = next((safe_extract(selector) for selector in price_selectors if safe_extract(selector) != 'N/A'), 'N/A')
            else:
                # Check for alternative price (e.g., from other sellers)
                alternative_price_selectors = [
                    '.a-price.a-spacing-top-small .a-offscreen',
                    '.a-price-range .a-price .a-offscreen'
                ]
                alternative_prices = [
                    safe_extract(selector) 
                    for selector in alternative_price_selectors 
                    if safe_extract(selector) != 'N/A'
                ]
                price = alternative_prices[0] if alternative_prices else 'Currently Unavailable'
            
            # Rating extraction
            rating = safe_extract('span.a-icon-alt', 'text')
            rating = rating.split()[0] if rating != 'N/A' else 'N/A'
            
            # Reviews extraction
            reviews = safe_extract('#acrCustomerReviewText', 'text')
            reviews = reviews.split()[0].replace(',', '') if reviews != 'N/A' else 'N/A'
            
            # Best Seller and Stock Status
            bestseller = 'Yes' if soup.select_one('#SalesRank') else 'No'
            in_stock = 'Yes' if is_available else 'No'
            
            # Sponsored Check
            sponsored = 'Yes' if soup.select_one('.a-badge-label') else 'No'
            
            return {
                'S.No': None,  # Will be filled later
                'ASIN': asin,
                'Link': url,
                'Title': title,
                'Price': price,
                'Availability': availability_text,  # Added availability text
                'Rating': rating,
                'Reviews': reviews,
                'BestSeller': bestseller,
                'In Stock': in_stock,
                'Sponsored': sponsored,
                'Bought Last Month': 'N/A',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        except requests.exceptions.RequestException as e:
            print(f"Request error for ASIN {asin}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error scraping ASIN {asin}: {e}")
            return None


# In[5]:


def scrape_asins(asin_list):
    """
    Scrape details for a list of ASINs with progress bar
    """
    scraper = AmazonScraper()
    results = []
    
    for index, asin in enumerate(tqdm(asin_list, desc="Scraping Products"), 1):
        product_details = scraper.get_product_details(asin)
        if product_details:
            product_details['S.No'] = index
            results.append(product_details)
    
    return results

def save_to_dataframe(results):
    """
    Convert results to pandas DataFrame
    """
    if not results:
        print("No results to save.")
        return None
    
    df = pd.DataFrame(results)
    return df


# In[7]:


# List of ASINs
asins = [
    'B000GISTZ4',
    'B091HTLXL3',
    'B0CLCLYJN1',
    'B09K3BXLBC',
    'B079SZJJDR',
    'B008BH7KKM',
    'B07X2QKVXH',
    'B0C2PT3V38',
    'B084H8LWC3',
    'B0CWGPP4JG',
    'B0B9YC7MSK',
    'B07MTQP3QB',
    'B07FNGNSMT',
    'B0CLCB1XCH',
    'B09CKLFZQP',
    'B07F2FH5NV',
    'B00CHJ45FI',
    'B07WZM3714',
    'B09Q3D6BGD',
    'B0DFH7LND3',
    'B0D9XXP4CT',
    'B0BRNL4LJ1',
    'B0D9BHX9MZ',
    'B00LLZ82O4',
    'B0BGSB5SQR',
    'B0C4LRGMD3',
    'B09VP6HL5J',
    'B07Q8JJLFL',
    'B0D13XGZK5',
    'B0BMWYR42N',
    'B0B97JMMK4',
    'B09Q3HFLPY',
    'B0D984BGJR',
    'B00KT2983Y',
    'B07YNL38ZY',
    'B0C592KZ7M',
    'B0CZDMHCQZ',
    'B07WH2YZ5R',
    'B0CKTVQT6G',
    'B0748HQW6C',
    'B075QHMZRQ',
    'B0757MM647',
    'B07WTBN75M',
    'B08KDCKSGK',
    'B08428SYDF',
    'B0854JP93Y',
    'B07XQB87RF',
    'B0C9TGQMWD',
    'B0BSGWKL3Z',
    'B07MBZK89S',
    'B09RTJQF47',
    'B0D8T5XTRQ',
    'B0DFTR7NF6',
    'B09PHLHS51',
    'B0D3HYDLF6',
    'B09HHL3QL3',
    'B09FLFHX1P',
    'B0D7LWQ974',
    'B07XYXC2HL',
    'B0C2VLD746',
    'B07SC24FGV',
    'B0943646ZS',
    'B0C3GSXMJT',
    'B09B72RJMB',
    'B0CP1TPZY9',
    'B0BG4SSQLT',
    'B083TZNB6W',
    'B0BPMFTYQD',
    'B0BD1RMHJ6',
    'B00KDFRUGY',
    'B081F7VD7Z',
    'B08XF3SCYJ',
    'B0C6KRWZDX',
    'B0BLSCFWL8',
    'B0BW18JWYF',
    'B00CHJ470G',
    'B09XXM7K79',
    'B0BPCPDJ46'
]

# Limit to the first 5 for testing
# asins = asins[:5]

# Print ASINs to verify
# print(asins)


# In[9]:


# Scrape products
results = scrape_asins(asins)

# Convert to DataFrame
df = save_to_dataframe(results)

# Display results
if df is not None:
    display(df)
    
    # Optional: Save to CSV
    df.to_csv('amazon_products.csv', index=False)


# In[39]:


df.to_clipboard()


# In[11]:


# Assuming your DataFrame is named 'df'
df['Price'] = df.apply(
    lambda row: 'Currently Unavailable' 
    if (row['Availability'] == 0) or pd.isna(row['Availability']) or row['Availability'] == '' 
    else row['Price'], axis=1
)


# In[12]:


df


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[17]:


# df.to_clipboard()


# In[18]:


# Step 1: Convert the entire column to string
df['Price'] = df['Price'].astype(str)

# Step 2: Remove single quotes, ₹ symbol, and commas
df['Price'] = df['Price'].str.replace("'", '', regex=False)  # Remove single quotes
df['Price'] = df['Price'].str.replace('₹', '', regex=False)  # Remove ₹ symbol
df['Price'] = df['Price'].str.replace(',', '', regex=False)  # Remove commas

# Step 3: Convert the cleaned strings to numeric
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')  # Coerce invalid values to NaN


# In[ ]:





# # pasting in the google sheet

# In[21]:


import pandas as pd
import numpy as np
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os
from requests import request
import json


# In[22]:


# Scopes for Google Sheets and Drive API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 
          'https://www.googleapis.com/auth/drive']


# In[23]:


def authenticate_google_sheets():
    token_path = 'token.pickle'
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)
    else:
        # Run the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',  # Download this from Google Cloud Console
            SCOPES
        )
        
        # This will open a browser for you to authorize
        credentials = flow.run_local_server(port=0)
        
        # Save the credentials for next run
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)
    
    # Build and return the Sheets service
    return build('sheets', 'v4', credentials=credentials)


# In[24]:


def prepare_data_for_sheets(df):
    # Convert DataFrame to list of lists with proper type handling
    def convert_value(val):
        # Handle different types of values
        if pd.isna(val):
            return ''  # Convert NaN to empty string
        elif isinstance(val, (int, float, str)):
            return str(val)  # Convert to string
        else:
            return str(val)  # Fallback to string conversion
    
    # Convert each row, ensuring all values are strings
    if isinstance(df, pd.DataFrame):
        values = []
        for _, row in data.iterrows():
            converted_row = [convert_value(val) for val in row]
            values.append(converted_row)
        return values
    return data


# # upload at the first blank cell of A column

# In[26]:


def find_first_blank_cell(spreadsheet_id, sheet_name='Python_dump'):
    """
    Find the first blank cell in column A of a Google Sheet.
    
    Args:
        spreadsheet_id (str): The ID of the Google Sheet.
        sheet_name (str, optional): Name of the sheet to search. Defaults to 'Sheet1'.
    
    Returns:
        str: The cell reference of the first blank cell (e.g., 'A2').
    """
    # Authenticate and get the Sheets service
    service = authenticate_google_sheets()
    
    try:
        # Read the entire column A
        range_name = f'{sheet_name}!A:A'
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, 
            range=range_name
        ).execute()
        
        # Get the values (if any)
        values = result.get('values', [])
        
        # Find the first blank row
        for row_index in range(len(values)):
            if len(values[row_index]) == 0 or values[row_index][0] == '':
                first_blank_cell = f'A{row_index + 1}'  # Cell reference
                print(f"First blank cell: {first_blank_cell}")
                return first_blank_cell
        
        # If no blank cells found in existing rows, return the next available row
        first_blank_cell = f'A{len(values) + 1}'
        print(f"First blank cell: {first_blank_cell}")
        return first_blank_cell
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def upload_dataframe_to_google_sheet(df, spreadsheet_id, sheet_name='Python_dump'):
    """
    Upload a DataFrame to a Google Sheet starting from the first blank cell in column A.
    
    Args:
        df (DataFrame): The DataFrame to upload.
        spreadsheet_id (str): The ID of the Google Sheet.
        sheet_name (str, optional): Name of the sheet. Defaults to 'Sheet1'.
    """
    try:
        # Authenticate Google Sheets
        service = authenticate_google_sheets()
        
        # Find the first blank cell in column A
        first_blank_cell = find_first_blank_cell(spreadsheet_id, sheet_name)
        if not first_blank_cell:
            print("Could not determine the first blank cell. Exiting upload.")
            return
        
        # Prepare data for upload
        values_to_upload = [df.columns.tolist()] + df.astype(str).values.tolist()
        
        # Prepare the request body
        body = {
            'values': values_to_upload
        }
        
        # Update the sheet starting at the first blank cell
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, 
            range=f'{sheet_name}!{first_blank_cell}',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Successfully uploaded {result.get('updatedCells', 0)} cells starting at {first_blank_cell}")
        return result
    
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None


# Usage in Jupyter Lab
def main():
    # Your Spreadsheet ID (from the Google Sheets URL)
    SPREADSHEET_ID = '11Nu3VdthNph-9HRrBHpKmNKIKDwRNwPVpEevJQu6FvQ'
    
    # # Example DataFrame (replace this with your actual DataFrame)
    # import pandas as pd
    # data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]}
    # df = pd.DataFrame(data)
    
    # Upload the DataFrame
    upload_dataframe_to_google_sheet(
        df, 
        spreadsheet_id=SPREADSHEET_ID,
        sheet_name='Python_dump'
    )

# Call the main function
main()


# In[ ]:





# In[ ]:





# In[ ]:




