import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json

def str_to_float_regex(s):
    """Convert string value to float, handling Brazilian number format"""
    if isinstance(s, (int, float)):
        return float(s)
    
    if not isinstance(s, str):
        return 0.0
        
    s = s.replace(" mi", "")
    match = re.search(r'-?[\d\.\,]+', s)
    if match:
        num_str = match.group(0)
        cleaned = num_str.replace('.', '').replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0

def get_fluxo_ddm_data():
    """Get flux data from local JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "export", "fluxo.json")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        print(f"Successfully read data from JSON: {len(data)} rows loaded")
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return []
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        return []

def scrape_fluxo_data():
    """Scrape flux data from dadosdemercado.com.br"""
    url = "https://www.dadosdemercado.com.br/fluxo"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'normal-table', 'id': 'flow'})
        
        if not table:
            print("Table not found on the webpage")
            return None
            
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
        data = []
        
        # Define key mappings for consistency
        key_mapping = {
            "Pessoa física": "PF",
            "Inst. Financeira": "IF"
        }
        
        for tr in table.find('tbody').find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all('td')]
            row_data = {header: cell for header, cell in zip(headers, cells)}
            
            # Apply key renaming
            row_data = {key_mapping.get(k, k): v for k, v in row_data.items()}
            
            # Convert all numeric fields to clean float values (except Data)
            clean_row = {}
            for key, value in row_data.items():
                if key == 'Data':
                    clean_row[key] = value
                else:
                    clean_row[key] = str_to_float_regex(value)
            
            data.append(clean_row)
        
        print(f"Successfully scraped {len(data)} records")
        return data
        
    except requests.RequestException as e:
        print(f"Failed to retrieve data from website: {e}")
        return None
    except Exception as e:
        print(f"Error scraping flux data: {e}")
        return None

def save_fluxo_data_json(data):
    """Save flux data to JSON file"""
    if not data:
        print("No data to save")
        return False
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_directory = os.path.join(current_dir, "export")
    os.makedirs(export_directory, exist_ok=True)
    full_path = os.path.join(export_directory, 'fluxo.json')
    
    try:
        with open(full_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)
        print(f"Data successfully saved to '{full_path}'")
        return True
    except Exception as e:
        print(f"Error saving JSON file: {str(e)}")
        return False

def update_fluxo_data():
    """Update flux data by scraping and saving to JSON"""
    print(f"Starting flux data update at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    data = scrape_fluxo_data()
    if data:
        success = save_fluxo_data_json(data)
        if success:
            print(f"Flux data update completed successfully at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print("Failed to save flux data")
            return False
    else:
        print("Failed to scrape flux data")
        return False

if __name__ == '__main__':
    update_fluxo_data()