import pandas as pd
import numpy as np
import random
from zipfile import ZipFile
from time import sleep
from numpy.linalg import multi_dot
import time
import yfinance as yf
from sklearn.cluster import KMeans
import json 
import os
from dolphindb import session
import warnings
import sys
from datetime import datetime, timedelta
from collections import Counter

warnings.filterwarnings('ignore')

# Add this block at the beginning of the file
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    from utils.dictionary import TICKERS_DICT
else:
    from ..dictionary import TICKERS_DICT

def connect_to_dolphindb():
    s = session()
    s.connect("46.202.149.154", 8848, "admin", "123456")
    return s

def fetch_data(s, table_name, tickers, start_date):
    s.run(f't = loadTable("dfs://yfs", "{table_name}")')
    query = f'''
    select Datetime, Symbol, AdjClose 
    from t 
    where Datetime > {start_date} and Symbol in {tickers}
    '''
    result = s.run(query)
    df = pd.DataFrame(result)
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df_pivot = df.pivot(index='Datetime', columns='Symbol', values='AdjClose')
    return df_pivot.sort_index()

def conta_dados_faltantes(df):
    return df.isna().sum().sort_values(ascending=False)

def encontraClusters(carteira, nclusters=4, period_ret=1, plotOn=True):
    retornos = 100 * carteira.pct_change(period_ret)
    stocks = retornos.columns
    X = 100 * np.array([[np.std(retornos[sto]), np.mean(retornos[sto])] for sto in stocks])
    N = nclusters
    kmeans = KMeans(n_clusters=N, random_state=0).fit(X)
    y_kmeans = kmeans.predict(X)
    centers = kmeans.cluster_centers_
    best = []
    for i in range(N):
        ind = retornos[retornos.columns[np.where(y_kmeans==i)[0]]].mean() / retornos[retornos.columns[np.where(y_kmeans==i)[0]]].std()
        best.append(ind[ind==np.max(ind)])
    rb = list(pd.DataFrame(best).columns)
    print("Ativos com Melhor Relação em Cada Cluster:", rb)
    return rb

def simulacaoMelhoresAtivosClusters(carteira, nret=20, list_clust=[4,7,10,20]):
    lista_ativos = []
    for i in range(1, nret):
        for j in list_clust:
            lista_ativos.append(encontraClusters(carteira=carteira, nclusters=j, period_ret=i, plotOn=False))
    di = dict(calculaQtdRepetidaDeAtivos(lista_ativos))
    sort_dict = dict(sorted(di.items(), key=lambda item: item[1], reverse=True)) 
    return sort_dict

def calculaQtdRepetidaDeAtivos(lista_ativos):
    total = [j for i in lista_ativos for j in i]
    r = Counter(total)
    sort_dict = dict(sorted(dict(r).items(), key=lambda item: item[1], reverse=True)) 
    return sort_dict

def simulacaoMelhoresAtivosMonteCarlo(dados, ret=1, sim_MC=500, tam_port=7, plotOn=False):
    df = dados.copy()
    nome_ibov = [a for a in df.columns if(a.startswith("BOVA") or a.startswith("WIN") or a.startswith("IND"))]
    
    if len(nome_ibov) == 0:
        return print("É preciso adicionar IND, WIND ou BOVA11 na carteira de ativos")
    else:
        nome_ibov = nome_ibov[0]
    
    p_ibov = df[nome_ibov]
    p_ibov = p_ibov / p_ibov.iloc[0]
    
    if len(nome_ibov) > 4:
        df.drop(nome_ibov, inplace=True, axis=1)
    else:
        print("O ativo BOVA11 não está contido dentro da massa de dados!")
    
    d = df.copy()
    retorno = df.pct_change(ret)
    retorno_acumulado = (1 + retorno).cumprod()
    retorno_acumulado.iloc[0] = 1
    
    carteira_saldo = {}

    for i in range(sim_MC):
        carteira = random.sample(list(d.columns), k=tam_port)
        carteira = 10000 * retorno_acumulado.loc[:, carteira]
        carteira['saldo'] = carteira.sum(axis=1)
        carteira_saldo[carteira['saldo'][-1]] = list(carteira.columns)
    
    port_acima_ibov = []
    ret_ibov = p_ibov[-1] * 10000 * tam_port
    
    sort_keys = sorted(carteira_saldo.keys(), reverse=True)
    
    cont = 0
    for i in sort_keys:
        if i > ret_ibov:
            cont += 1
            port_acima_ibov.append(carteira_saldo[i])
    
    top_5 = pd.DataFrame()
    for i in sort_keys[:6]:
        top_5[i] = carteira_saldo[i]
    top_5 = top_5.iloc[:-1,:]
    
    freq = calculaQtdRepetidaDeAtivos(port_acima_ibov)
    print(f'Tam Port = {tam_port}, retorno = {ret}, Tivemos {cont} portfólios acima do IBOV de um total de {sim_MC}')
    
    return carteira_saldo, port_acima_ibov, freq, top_5

def mlnsupport(data, nret_=20, list_clust_=[3,4,5]):
    c1 = simulacaoMelhoresAtivosClusters(data, nret=nret_, list_clust=list_clust_)
    sort_orders = sorted(c1.items(), key=lambda x: x[1], reverse=True)
    df_res = pd.DataFrame(sort_orders, columns=['ATIVO', 'FREQ'])
    return df_res.to_dict(orient='records')

def mcport(data, ret=5, n_sim_mc=1200, tam_port_=4):
    try:
        carteira_saldo, port_acima_ibov, freq, top_5 = simulacaoMelhoresAtivosMonteCarlo(data, ret=ret, 
                                                                                         sim_MC=n_sim_mc, 
                                                                                         tam_port=tam_port_)
        return freq
    except Exception as e:
        print(f"Error in mcport: {str(e)}")
        return None

def update_quant_port_data():
    s = connect_to_dolphindb()
    tickers = TICKERS_DICT.get('IBOV', [])
    now = datetime.now()
    start_date = (now - timedelta(days=365)).strftime("%Y.%m.%d")

    data = fetch_data(s, "stockdata_1d", tickers, start_date)

    if 'BOVA11' not in data.columns:
        print("Warning: BOVA11 not found in the data. Adding a placeholder column.")
        data['BOVA11'] = data.mean(axis=1)

    mlnsupport_data = mlnsupport(data)
    mcport_data = mcport(data)

    quant_port_data = {
        "mlnsupport": mlnsupport_data,
        "mcport": mcport_data
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_directory = os.path.join(script_dir, "export")
    os.makedirs(export_directory, exist_ok=True)
    output_file_path = os.path.join(export_directory, "quant_port_data.json")

    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(quant_port_data, json_file, indent=2, default=str)

    print(f"Quantitative portfolio data updated and saved to {output_file_path}")
    print(f"Quant port data updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def get_quant_port_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "export", "quant_port_data.json")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            quant_port_data = json.load(json_file)
        print(f"Quant port data loaded: {quant_port_data}")
        return quant_port_data
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return {"error": "Data not found"}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {json_file_path}")
        return {"error": "Invalid data"}

if __name__ == "__main__":
    update_quant_port_data()