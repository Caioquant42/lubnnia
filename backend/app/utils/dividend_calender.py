import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import unidecode
import os

def fetch_and_save_dividend_data():
    # URL of the webpage to scrape
    url = 'https://www.dadosdemercado.com.br/agenda-de-dividendos'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the table
    tabela = soup.find('table', class_='normal-table')

    # Extract headers
    cabecalhos = [unidecode.unidecode(th.text.strip()) for th in tabela.find('thead').find_all('th')]

    # Extract row data
    dados = []
    for linha in tabela.find('tbody').find_all('tr'):
        linha_dados = [unidecode.unidecode(td.text.strip()) for td in linha.find_all('td')]
        dados.append(linha_dados)

    # Create a DataFrame
    df = pd.DataFrame(dados, columns=cabecalhos)

    # Convert DataFrame to dictionary
    data_dict = df.to_dict(orient='records')

    # Get the absolute path of the current script directory
    current_directory = os.path.dirname(os.path.abspath(__file__))
    filename = f'dividend_calender.json'
    file_path = os.path.join(current_directory, 'export', filename) # Create the full path

    # Save the data as a JSON file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=4)

    print(f"Data successfully saved to {file_path}")
    return file_path    

if __name__ == "__main__":
    fetch_and_save_dividend_data()
