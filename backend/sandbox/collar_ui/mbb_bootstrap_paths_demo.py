"""
Exemplo simples de uso do Moving Block Bootstrap (MBB) para gerar
caminhos de preço de um ativo e plotar as trajetórias.

Uso esperado:
    python mbb_bootstrap_paths_demo.py
"""

import sys
from typing import Tuple, Dict
from pathlib import Path
import importlib.util
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt


def _load_module_from_path(module_name: str, file_path: Path):
    """Carrega um módulo Python diretamente de um caminho de arquivo, sem depender de pacotes."""
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível criar spec para {module_name} em {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


BASE_DIR = Path(__file__).resolve().parent
# Go up from sandbox/collar_ui to backend, then to app/utils/mbb
# BASE_DIR.parent = sandbox, BASE_DIR.parent.parent = backend
MBB_DIR = BASE_DIR.parent.parent / "app" / "utils" / "mbb"

_mbb_core_mod = _load_module_from_path("mbb_core_local", MBB_DIR / "mbb_core.py")
_data_gatherer_mod = _load_module_from_path("data_gatherer_local", MBB_DIR / "data_gatherer.py")

MBBCore = _mbb_core_mod.MBBCore
DataGatherer = _data_gatherer_mod.DataGatherer


def business_days_between(start_date: datetime, end_date: datetime) -> int:
    """Calcula o número de dias úteis entre duas datas."""
    return int(np.busday_count(start_date.date(), end_date.date()))


def ask_user_inputs() -> Tuple[str, Dict, int]:
    """
    Pergunta ao usuário os parâmetros da estrutura COLLAR UI.
    
    Retorna:
        - ticker: str
        - estrutura_params: dict com todos os parâmetros da estrutura
        - n_caminhos: int
    """
    ticker = input("Digite o ticker do ativo (ex: PETR4): ").strip().upper()
    if not ticker:
        print("Ticker não pode ser vazio.")
        sys.exit(1)

    try:
        S0 = float(input("Digite o preço inicial S0 (ex: 38.50): ").strip())
        if S0 <= 0:
            raise ValueError
    except ValueError:
        print("Preço inicial S0 inválido. Deve ser um número positivo.")
        sys.exit(1)

    try:
        strike_put_pct = float(input("Strike Put em % do S0 (ex: 90.0 para 90%): ").strip())
        if strike_put_pct <= 0 or strike_put_pct >= 100:
            raise ValueError
        strike_put = strike_put_pct / 100.0
    except ValueError:
        print("Strike Put inválido. Deve ser um número entre 0 e 100.")
        sys.exit(1)

    try:
        strike_call_pct = float(input("Strike Call em % do S0 (ex: 107.5 para 107.5%): ").strip())
        if strike_call_pct <= 0:
            raise ValueError
        strike_call = strike_call_pct / 100.0
    except ValueError:
        print("Strike Call inválido. Deve ser um número positivo.")
        sys.exit(1)

    try:
        data_venc_str = input("Data de vencimento (DD-MM-YYYY, ex: 12-03-2026): ").strip()
        data_venc = datetime.strptime(data_venc_str, "%d-%m-%Y")
        data_atual = datetime.now()
        if data_venc <= data_atual:
            raise ValueError("Data de vencimento deve ser futura.")
    except ValueError as e:
        print(f"Data de vencimento inválida: {e}")
        sys.exit(1)

    # Calcula dias úteis até o vencimento
    dias_uteis = business_days_between(data_atual, data_venc)
    if dias_uteis <= 0:
        print("Data de vencimento muito próxima ou no passado.")
        sys.exit(1)

    try:
        barreira_pct = float(input("Barreira de ativação Up&In em % do S0 (ex: 144.0 para 144%): ").strip())
        if barreira_pct <= 0:
            raise ValueError
        barreira_ativacao = barreira_pct / 100.0
    except ValueError:
        print("Barreira de ativação inválida. Deve ser um número positivo.")
        sys.exit(1)

    # Calcula automaticamente os ganhos máximos:
    # 1. Ganho máximo se barreira ativada = diferença entre strike call e S0
    ganho_max_ativado = strike_call - 1.0
    
    # 2. Ganho máximo se barreira NÃO ativada = diferença entre barreira e S0, menos 0.01% de margem
    # para garantir que a barreira não foi atingida
    ganho_max_nao_ativado = barreira_ativacao - 1.0 - 0.0001
    
    print(f"\n✓ Ganho máximo se barreira ativada: {ganho_max_ativado*100:.2f}% (calculado automaticamente)")
    print(f"✓ Ganho máximo se barreira NÃO ativada: {ganho_max_nao_ativado*100:.2f}% (calculado automaticamente)")

    # Prejuízo máximo calculado a partir do strike put
    prejuizo_maximo = 1.0 - strike_put

    caminhos_str = input("Número de caminhos de bootstrap [padrão = 1000]: ").strip()
    if caminhos_str == "":
        n_caminhos = 1000
    else:
        try:
            n_caminhos = int(caminhos_str)
            if n_caminhos <= 0:
                raise ValueError
        except ValueError:
            print("Número de caminhos inválido.")
            sys.exit(1)

    estrutura_params = {
        "S0": S0,
        "strike_put": strike_put,
        "strike_call": strike_call,
        "data_vencimento": data_venc,
        "dias_uteis": dias_uteis,
        "barreira_ativacao": barreira_ativacao,
        "ganho_max_ativado": ganho_max_ativado,
        "ganho_max_nao_ativado": ganho_max_nao_ativado,
        "prejuizo_maximo": prejuizo_maximo,
    }

    return ticker, estrutura_params, n_caminhos


def get_price_series(ticker: str, dias_uteis: int) -> np.ndarray:
    """
    Baixa a série de preços de fechamento do ativo usando DataGatherer.

    Retorna:
        - série de preços (np.ndarray)
    """
    dg = DataGatherer(use_monte_carlo_selection=False)

    # Calcula período necessário: pelo menos 3x o horizonte ou horizonte + 20 dias
    # Para períodos muito longos, usa start_date/end_date em vez de period
    periodo_dias = max(dias_uteis * 3, dias_uteis + 20)
    
    # Se o período for muito longo (> 2 anos), usa start_date/end_date
    if periodo_dias > 500:
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(periodo_dias * 1.5))  # Buffer de 50% para garantir dias úteis
        df = dg.get_data(
            asset_list=[ticker], 
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
    else:
        period_str = f"{periodo_dias}d"
        df = dg.get_data(asset_list=[ticker], period=period_str)
    
    if df.empty:
        print(f"Não foi possível baixar dados para o ativo {ticker}.")
        sys.exit(1)

    col_name = df.columns[0]
    prices = df[col_name].values.astype(float)

    # Verifica se há dados suficientes, mas permite continuar com aviso se houver pelo menos alguns dados
    if len(prices) < dias_uteis:
        if len(prices) < 20:
            print(
                f"ERRO: Número de observações ({len(prices)}) é muito pequeno. "
                f"Necessário pelo menos {dias_uteis} dias úteis."
            )
            sys.exit(1)
        else:
            print(
                f"AVISO: Número de observações ({len(prices)}) é menor que o horizonte "
                f"de {dias_uteis} dias úteis. A simulação continuará com os dados disponíveis, "
                f"mas os resultados podem ser menos confiáveis."
            )

    return prices


def calculate_collar_ui_payoffs(
    paths: np.ndarray,
    estrutura_params: Dict,
) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """
    Calcula os payoffs da estrutura COLLAR UI para cada caminho.
    
    Parâmetros:
    -----------
    paths : np.ndarray
        Array (n_caminhos, dias_uteis + 1) com preços simulados
    estrutura_params : dict
        Parâmetros da estrutura COLLAR UI
        
    Retorna:
    --------
    payoffs : np.ndarray
        Payoffs em % para cada caminho
    cenarios : np.ndarray
        Array indicando o cenário de cada caminho (0=perda, 1=ganho_sem_barreira, 2=ganho_com_barreira)
    stats : dict
        Estatísticas dos cenários
    """
    S0 = estrutura_params["S0"]
    strike_put = estrutura_params["strike_put"]
    barreira_ativacao = estrutura_params["barreira_ativacao"]
    ganho_max_ativado = estrutura_params["ganho_max_ativado"]
    ganho_max_nao_ativado = estrutura_params["ganho_max_nao_ativado"]
    prejuizo_maximo = estrutura_params["prejuizo_maximo"]
    
    n_caminhos, horizonte = paths.shape
    payoffs = np.zeros(n_caminhos)
    cenarios = np.zeros(n_caminhos, dtype=int)  # 0=perda, 1=ganho_sem_barreira, 2=ganho_com_barreira
    
    # Níveis absolutos
    barreira_abs = S0 * barreira_ativacao
    strike_put_abs = S0 * strike_put
    
    for i in range(n_caminhos):
        path = paths[i, :]
        preco_final = path[-1]
        
        # Verifica se a barreira foi atingida em algum momento
        barreira_atingida = np.any(path >= barreira_abs)
        
        # Calcula retorno simples
        retorno = (preco_final - S0) / S0
        
        if preco_final < S0:
            # Cenário de perda
            # Perda limitada pelo strike put
            payoff = max(retorno, -prejuizo_maximo)
            cenarios[i] = 0
        else:
            # Cenário de ganho
            if barreira_atingida:
                # Barreira foi atingida: ganho limitado a ganho_max_ativado
                payoff = min(retorno, ganho_max_ativado)
                cenarios[i] = 2
            else:
                # Barreira NÃO foi atingida: ganho limitado a ganho_max_nao_ativado
                payoff = min(retorno, ganho_max_nao_ativado)
                cenarios[i] = 1
        
        payoffs[i] = payoff
    
    # Estatísticas
    n_perda = np.sum(cenarios == 0)
    n_ganho_sem_barreira = np.sum(cenarios == 1)
    n_ganho_com_barreira = np.sum(cenarios == 2)
    
    stats = {
        "n_perda": n_perda,
        "n_ganho_sem_barreira": n_ganho_sem_barreira,
        "n_ganho_com_barreira": n_ganho_com_barreira,
        "pct_perda": n_perda / n_caminhos * 100,
        "pct_ganho_sem_barreira": n_ganho_sem_barreira / n_caminhos * 100,
        "pct_ganho_com_barreira": n_ganho_com_barreira / n_caminhos * 100,
        "payoff_medio": np.mean(payoffs),
        "payoff_mediano": np.median(payoffs),
        "payoff_std": np.std(payoffs),
        "payoff_min": np.min(payoffs),
        "payoff_max": np.max(payoffs),
    }
    
    return payoffs, cenarios, stats


def generate_mbb_paths(
    prices: np.ndarray,
    S0: float,
    dias_uteis: int,
    n_caminhos: int,
) -> np.ndarray:
    """
    Gera caminhos de preço usando Moving Block Bootstrap (MBB).

    Passos:
      1. Calcula retornos logarítmicos (log returns).
      2. Aplica MBB (MBBCore.moving_block_bootstrap) para gerar n_caminhos amostras.
      3. Constrói caminhos de preço aplicando cumulativamente os retornos logarítmicos sobre S0.

    Retorna:
        paths: array (n_caminhos, dias_uteis + 1) com preços simulados,
               incluindo o ponto inicial S0 na coluna 0.
    """
    # Retornos logarítmicos: log(P_t / P_{t-1}) = log(P_t) - log(P_{t-1})
    returns = np.diff(np.log(prices))

    mbb_core = MBBCore()

    # Gera amostras de retornos logarítmicos com blocos móveis
    bootstrap_samples = mbb_core.moving_block_bootstrap(
        returns,
        n_bootstrap=n_caminhos,
        sample_size=dias_uteis,
    )

    # Constrói os caminhos de preço usando retornos logarítmicos: P_t = P_0 * exp(sum(log_returns))
    # paths_sem_S0 tem shape (n_caminhos, dias_uteis)
    paths_sem_S0 = S0 * np.exp(np.cumsum(bootstrap_samples, axis=1))

    # Inclui S0 na coluna inicial para ter o ponto t=0
    paths = np.zeros((n_caminhos, dias_uteis + 1), dtype=float)
    paths[:, 0] = S0
    paths[:, 1:] = paths_sem_S0

    return paths


def plot_paths(
    paths: np.ndarray,
    payoffs: np.ndarray,
    cenarios: np.ndarray,
    ticker: str,
    estrutura_params: Dict,
    max_paths_to_plot: int = 200,
) -> None:
    """
    Plota os caminhos de preço gerados e os payoffs da estrutura COLLAR UI.
    """
    S0 = estrutura_params["S0"]
    dias_uteis = estrutura_params["dias_uteis"]
    barreira_ativacao = estrutura_params["barreira_ativacao"]
    strike_put = estrutura_params["strike_put"]
    strike_call = estrutura_params["strike_call"]
    
    n_caminhos, horizonte = paths.shape
    n_plot = min(n_caminhos, max_paths_to_plot)

    x = np.arange(horizonte)  # 0 .. dias_uteis
    
    # Níveis de referência
    barreira_abs = S0 * barreira_ativacao
    strike_put_abs = S0 * strike_put
    strike_call_abs = S0 * strike_call

    # Criar figura com subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1])

    # Subplot 1: Caminhos de preço
    cores_cenarios = {0: "red", 1: "green", 2: "orange"}
    labels_cenarios = {0: "Perda", 1: "Ganho (sem barreira)", 2: "Ganho (barreira ativada)"}
    
    for i in range(n_plot):
        cor = cores_cenarios.get(cenarios[i], "steelblue")
        alpha = 0.15 if cenarios[i] == 0 else 0.2
        ax1.plot(x, paths[i], color=cor, alpha=alpha, linewidth=0.8)

    # Linhas de referência
    ax1.axhline(y=S0, color="black", linestyle="--", linewidth=1.5, label=f"S0 = R$ {S0:.2f}")
    ax1.axhline(y=barreira_abs, color="orange", linestyle="--", linewidth=1.5, 
                label=f"Barreira Up&In = {barreira_ativacao*100:.1f}% (R$ {barreira_abs:.2f})")
    ax1.axhline(y=strike_put_abs, color="red", linestyle="--", linewidth=1.5, 
                label=f"Strike Put = {strike_put*100:.1f}% (R$ {strike_put_abs:.2f})")
    ax1.axhline(y=strike_call_abs, color="blue", linestyle="--", linewidth=1.5, 
                label=f"Strike Call = {strike_call*100:.1f}% (R$ {strike_call_abs:.2f})")

    ax1.set_title(
        f"COLLAR UI - {ticker} | {n_caminhos} caminhos simulados | {dias_uteis} dias úteis\n"
        f"Barreira: {barreira_ativacao*100:.1f}% | Put: {strike_put*100:.1f}% | Call: {strike_call*100:.1f}%",
        fontsize=12
    )
    ax1.set_xlabel("Dias úteis à frente")
    ax1.set_ylabel("Preço simulado (R$)")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="best", fontsize=9)

    # Subplot 2: Distribuição de payoffs
    cores_hist = [cores_cenarios[i] for i in cenarios[:n_plot]]
    ax2.hist(payoffs * 100, bins=50, alpha=0.7, color="steelblue", edgecolor="black")
    ax2.axvline(x=0, color="black", linestyle="-", linewidth=1, alpha=0.5)
    ax2.axvline(x=np.mean(payoffs) * 100, color="red", linestyle="--", linewidth=2, 
                label=f"Média: {np.mean(payoffs)*100:.2f}%")
    ax2.axvline(x=np.median(payoffs) * 100, color="green", linestyle="--", linewidth=2, 
                label=f"Mediana: {np.median(payoffs)*100:.2f}%")
    
    ax2.set_title("Distribuição de Payoffs da Estrutura COLLAR UI", fontsize=12)
    ax2.set_xlabel("Payoff (%)")
    ax2.set_ylabel("Frequência")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best", fontsize=9)

    plt.tight_layout()
    plt.show()


def print_statistics(payoffs: np.ndarray, cenarios: np.ndarray, estrutura_params: Dict) -> None:
    """Imprime estatísticas detalhadas da simulação."""
    stats = {
        "n_perda": np.sum(cenarios == 0),
        "n_ganho_sem_barreira": np.sum(cenarios == 1),
        "n_ganho_com_barreira": np.sum(cenarios == 2),
    }
    n_total = len(cenarios)
    
    print("\n" + "="*70)
    print("ESTATÍSTICAS DA SIMULAÇÃO - ESTRUTURA COLLAR UI")
    print("="*70)
    print(f"\nParâmetros da Estrutura:")
    print(f"  S0: R$ {estrutura_params['S0']:.2f}")
    print(f"  Strike Put: {estrutura_params['strike_put']*100:.2f}% (R$ {estrutura_params['S0'] * estrutura_params['strike_put']:.2f})")
    print(f"  Strike Call: {estrutura_params['strike_call']*100:.2f}% (R$ {estrutura_params['S0'] * estrutura_params['strike_call']:.2f})")
    print(f"  Barreira Up&In: {estrutura_params['barreira_ativacao']*100:.2f}% (R$ {estrutura_params['S0'] * estrutura_params['barreira_ativacao']:.2f})")
    print(f"  Prejuízo Máximo: {estrutura_params['prejuizo_maximo']*100:.2f}%")
    print(f"  Ganho Máximo (barreira ativada): {estrutura_params['ganho_max_ativado']*100:.2f}%")
    print(f"  Ganho Máximo (barreira NÃO ativada): {estrutura_params['ganho_max_nao_ativado']*100:.2f}%")
    print(f"  Dias úteis até vencimento: {estrutura_params['dias_uteis']}")
    print(f"  Data de vencimento: {estrutura_params['data_vencimento'].strftime('%d-%m-%Y')}")
    
    print(f"\nCenários:")
    print(f"  Perda: {stats['n_perda']} caminhos ({stats['n_perda']/n_total*100:.2f}%)")
    print(f"  Ganho (sem barreira): {stats['n_ganho_sem_barreira']} caminhos ({stats['n_ganho_sem_barreira']/n_total*100:.2f}%)")
    print(f"  Ganho (barreira ativada): {stats['n_ganho_com_barreira']} caminhos ({stats['n_ganho_com_barreira']/n_total*100:.2f}%)")
    
    print(f"\nEstatísticas dos Payoffs:")
    print(f"  Média: {np.mean(payoffs)*100:.2f}%")
    print(f"  Mediana: {np.median(payoffs)*100:.2f}%")
    print(f"  Desvio Padrão: {np.std(payoffs)*100:.2f}%")
    print(f"  Mínimo: {np.min(payoffs)*100:.2f}%")
    print(f"  Máximo: {np.max(payoffs)*100:.2f}%")
    print(f"  Percentil 5%: {np.percentile(payoffs, 5)*100:.2f}%")
    print(f"  Percentil 95%: {np.percentile(payoffs, 95)*100:.2f}%")
    
    print("\n" + "="*70 + "\n")


def main() -> None:
    ticker, estrutura_params, n_caminhos = ask_user_inputs()
    
    S0 = estrutura_params["S0"]
    dias_uteis = estrutura_params["dias_uteis"]
    
    print(f"\nBaixando dados históricos para {ticker}...")
    prices = get_price_series(ticker, dias_uteis)
    
    print(f"Gerando {n_caminhos} caminhos de bootstrap para {dias_uteis} dias úteis...")
    paths = generate_mbb_paths(prices, S0, dias_uteis, n_caminhos)
    
    print("Calculando payoffs da estrutura COLLAR UI...")
    payoffs, cenarios, stats = calculate_collar_ui_payoffs(paths, estrutura_params)
    
    print_statistics(payoffs, cenarios, estrutura_params)
    
    print("Gerando gráficos...")
    plot_paths(paths, payoffs, cenarios, ticker, estrutura_params)


if __name__ == "__main__":
    main()


