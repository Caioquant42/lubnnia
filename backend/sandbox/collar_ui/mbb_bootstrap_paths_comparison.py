"""
Comparação de duas estruturas COLLAR UI usando Moving Block Bootstrap (MBB).

Este script permite comparar duas estruturas COLLAR UI diferentes e gerar
um relatório detalhado com métricas comparativas e visualizações.

Uso esperado:
    python mbb_bootstrap_paths_comparison.py
"""

import sys
from typing import Tuple, Dict, List
from pathlib import Path
import importlib.util
from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


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


def ask_collar_ui_params(estrutura_num: int) -> Tuple[str, Dict]:
    """
    Pergunta ao usuário os parâmetros de uma estrutura COLLAR UI.
    
    Args:
        estrutura_num: Número da estrutura (1 ou 2)
    
    Returns:
        tuple: (ticker, dict com todos os parâmetros da estrutura)
    """
    print(f"\n{'='*70}")
    print(f"ESTRUTURA COLLAR UI #{estrutura_num}")
    print(f"{'='*70}")
    
    ticker = input(f"Digite o ticker do ativo para Estrutura #{estrutura_num} (ex: PETR4): ").strip().upper()
    if not ticker:
        print("Ticker não pode ser vazio.")
        sys.exit(1)
    
    try:
        S0 = float(input(f"Preço inicial S0 (ex: 38.50): ").strip())
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

    return ticker, estrutura_params


def ask_user_inputs() -> Tuple[str, Dict, str, Dict, int]:
    """
    Pergunta ao usuário os parâmetros para comparação de duas estruturas COLLAR UI.
    
    Returns:
        - ticker_A: str - ticker do ativo da estrutura A
        - estrutura_params_1: dict com parâmetros da primeira estrutura
        - ticker_B: str - ticker do ativo da estrutura B
        - estrutura_params_2: dict com parâmetros da segunda estrutura
        - n_caminhos: int
    """
    ticker_A, estrutura_params_1 = ask_collar_ui_params(1)
    ticker_B, estrutura_params_2 = ask_collar_ui_params(2)

    caminhos_str = input("\nNúmero de caminhos de bootstrap [padrão = 1000]: ").strip()
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

    return ticker_A, estrutura_params_1, ticker_B, estrutura_params_2, n_caminhos


def get_price_series(ticker: str, dias_uteis: int) -> np.ndarray:
    """Baixa a série de preços de fechamento do ativo usando DataGatherer."""
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
    
    Returns:
        payoffs: Payoffs em % para cada caminho
        cenarios: Array indicando o cenário (0=perda, 1=ganho_sem_barreira, 2=ganho_com_barreira)
        stats: Estatísticas dos cenários
    """
    S0 = estrutura_params["S0"]
    strike_put = estrutura_params["strike_put"]
    barreira_ativacao = estrutura_params["barreira_ativacao"]
    ganho_max_ativado = estrutura_params["ganho_max_ativado"]
    ganho_max_nao_ativado = estrutura_params["ganho_max_nao_ativado"]
    prejuizo_maximo = estrutura_params["prejuizo_maximo"]
    
    n_caminhos, horizonte = paths.shape
    payoffs = np.zeros(n_caminhos)
    cenarios = np.zeros(n_caminhos, dtype=int)
    
    barreira_abs = S0 * barreira_ativacao
    
    for i in range(n_caminhos):
        path = paths[i, :]
        preco_final = path[-1]
        
        barreira_atingida = np.any(path >= barreira_abs)
        retorno = (preco_final - S0) / S0
        
        if preco_final < S0:
            payoff = max(retorno, -prejuizo_maximo)
            cenarios[i] = 0
        else:
            if barreira_atingida:
                payoff = min(retorno, ganho_max_ativado)
                cenarios[i] = 2
            else:
                payoff = min(retorno, ganho_max_nao_ativado)
                cenarios[i] = 1
        
        payoffs[i] = payoff
    
    stats = {
        "n_perda": np.sum(cenarios == 0),
        "n_ganho_sem_barreira": np.sum(cenarios == 1),
        "n_ganho_com_barreira": np.sum(cenarios == 2),
        "pct_perda": np.sum(cenarios == 0) / n_caminhos * 100,
        "pct_ganho_sem_barreira": np.sum(cenarios == 1) / n_caminhos * 100,
        "pct_ganho_com_barreira": np.sum(cenarios == 2) / n_caminhos * 100,
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
    """Gera caminhos de preço usando Moving Block Bootstrap (MBB)."""
    returns = np.diff(prices) / prices[:-1]
    mbb_core = MBBCore()

    bootstrap_samples = mbb_core.moving_block_bootstrap(
        returns,
        n_bootstrap=n_caminhos,
        sample_size=dias_uteis,
    )

    paths_sem_S0 = S0 * np.cumprod(1.0 + bootstrap_samples, axis=1)
    paths = np.zeros((n_caminhos, dias_uteis + 1), dtype=float)
    paths[:, 0] = S0
    paths[:, 1:] = paths_sem_S0

    return paths


def calculate_comparison_metrics(
    payoffs_A: np.ndarray,
    payoffs_B: np.ndarray,
    cenarios_A: np.ndarray,
    cenarios_B: np.ndarray,
    estrutura_params_A: Dict,
    estrutura_params_B: Dict,
) -> Dict:
    """
    Calcula todas as métricas comparativas entre duas estruturas.
    
    Returns:
        dict com todas as métricas comparativas
    """
    # Métricas básicas
    expected_return_A = np.mean(payoffs_A)
    expected_return_B = np.mean(payoffs_B)
    std_A = np.std(payoffs_A)
    std_B = np.std(payoffs_B)
    
    # Sharpe Ratio (assumindo taxa livre de risco = 0)
    sharpe_A = expected_return_A / std_A if std_A > 0 else 0
    sharpe_B = expected_return_B / std_B if std_B > 0 else 0
    
    # Sortino Ratio (volatilidade negativa)
    downside_std_A = np.std(payoffs_A[payoffs_A < 0]) if np.any(payoffs_A < 0) else 0
    downside_std_B = np.std(payoffs_B[payoffs_B < 0]) if np.any(payoffs_B < 0) else 0
    sortino_A = expected_return_A / downside_std_A if downside_std_A > 0 else 0
    sortino_B = expected_return_B / downside_std_B if downside_std_B > 0 else 0
    
    # Probabilidades de cenários
    prob_perda_A = np.sum(cenarios_A == 0) / len(cenarios_A)
    prob_perda_B = np.sum(cenarios_B == 0) / len(cenarios_B)
    prob_ganho_sem_barreira_A = np.sum(cenarios_A == 1) / len(cenarios_A)
    prob_ganho_sem_barreira_B = np.sum(cenarios_B == 1) / len(cenarios_B)
    prob_ganho_com_barreira_A = np.sum(cenarios_A == 2) / len(cenarios_A)
    prob_ganho_com_barreira_B = np.sum(cenarios_B == 2) / len(cenarios_B)
    
    # Probabilidade de ganho positivo
    prob_ganho_positivo_A = np.sum(payoffs_A > 0) / len(payoffs_A)
    prob_ganho_positivo_B = np.sum(payoffs_B > 0) / len(payoffs_B)
    
    # Ganho esperado condicional (dado que há ganho)
    ganho_esperado_condicional_A = np.mean(payoffs_A[payoffs_A > 0]) if np.any(payoffs_A > 0) else 0
    ganho_esperado_condicional_B = np.mean(payoffs_B[payoffs_B > 0]) if np.any(payoffs_B > 0) else 0
    
    # Value at Risk (VaR) e Conditional VaR (CVaR)
    VaR_5_A = np.percentile(payoffs_A, 5)
    VaR_5_B = np.percentile(payoffs_B, 5)
    CVaR_5_A = np.mean(payoffs_A[payoffs_A <= VaR_5_A]) if np.any(payoffs_A <= VaR_5_A) else VaR_5_A
    CVaR_5_B = np.mean(payoffs_B[payoffs_B <= VaR_5_B]) if np.any(payoffs_B <= VaR_5_B) else VaR_5_B
    
    # Percentis
    percentis = [5, 25, 50, 75, 95]
    percentis_A = {p: np.percentile(payoffs_A, p) for p in percentis}
    percentis_B = {p: np.percentile(payoffs_B, p) for p in percentis}
    
    # Probabilidade de perda máxima
    prob_perda_max_A = np.sum(payoffs_A <= -estrutura_params_A['prejuizo_maximo']) / len(payoffs_A)
    prob_perda_max_B = np.sum(payoffs_B <= -estrutura_params_B['prejuizo_maximo']) / len(payoffs_B)
    
    # Probabilidade de atingir ganho máximo
    prob_ganho_max_ativado_A = np.sum(payoffs_A >= estrutura_params_A['ganho_max_ativado']) / len(payoffs_A)
    prob_ganho_max_ativado_B = np.sum(payoffs_B >= estrutura_params_B['ganho_max_ativado']) / len(payoffs_B)
    prob_ganho_max_nao_ativado_A = np.sum(
        (payoffs_A >= estrutura_params_A['ganho_max_nao_ativado']) & (cenarios_A == 1)
    ) / len(payoffs_A)
    prob_ganho_max_nao_ativado_B = np.sum(
        (payoffs_B >= estrutura_params_B['ganho_max_nao_ativado']) & (cenarios_B == 1)
    ) / len(payoffs_B)
    
    return {
        "expected_return": {"A": expected_return_A, "B": expected_return_B},
        "std": {"A": std_A, "B": std_B},
        "sharpe_ratio": {"A": sharpe_A, "B": sharpe_B},
        "sortino_ratio": {"A": sortino_A, "B": sortino_B},
        "prob_perda": {"A": prob_perda_A, "B": prob_perda_B},
        "prob_ganho_sem_barreira": {"A": prob_ganho_sem_barreira_A, "B": prob_ganho_sem_barreira_B},
        "prob_ganho_com_barreira": {"A": prob_ganho_com_barreira_A, "B": prob_ganho_com_barreira_B},
        "prob_ganho_positivo": {"A": prob_ganho_positivo_A, "B": prob_ganho_positivo_B},
        "ganho_esperado_condicional": {"A": ganho_esperado_condicional_A, "B": ganho_esperado_condicional_B},
        "VaR_5": {"A": VaR_5_A, "B": VaR_5_B},
        "CVaR_5": {"A": CVaR_5_A, "B": CVaR_5_B},
        "percentis": {"A": percentis_A, "B": percentis_B},
        "prob_perda_max": {"A": prob_perda_max_A, "B": prob_perda_max_B},
        "prob_ganho_max_ativado": {"A": prob_ganho_max_ativado_A, "B": prob_ganho_max_ativado_B},
        "prob_ganho_max_nao_ativado": {"A": prob_ganho_max_nao_ativado_A, "B": prob_ganho_max_nao_ativado_B},
    }


def print_comparison_report(
    payoffs_A: np.ndarray,
    payoffs_B: np.ndarray,
    cenarios_A: np.ndarray,
    cenarios_B: np.ndarray,
    ticker_A: str,
    ticker_B: str,
    estrutura_params_A: Dict,
    estrutura_params_B: Dict,
    metrics: Dict,
) -> None:
    """Imprime relatório comparativo detalhado."""
    print("\n" + "="*80)
    print("RELATÓRIO COMPARATIVO - ESTRUTURAS COLLAR UI")
    print("="*80)
    
    # Parâmetros das estruturas
    print("\n" + "-"*80)
    print("PARÂMETROS DAS ESTRUTURAS")
    print("-"*80)
    
    params_table = pd.DataFrame({
        "Parâmetro": [
            "Ticker",
            "S0",
            "Strike Put (%)",
            "Strike Call (%)",
            "Barreira Up&In (%)",
            "Prejuízo Máximo (%)",
            "Ganho Máx. (Barreira Ativada) (%)",
            "Ganho Máx. (Barreira NÃO Ativada) (%)",
            "Dias Úteis",
            "Data Vencimento",
        ],
        "Estrutura A": [
            ticker_A,
            f"R$ {estrutura_params_A['S0']:.2f}",
            f"{estrutura_params_A['strike_put']*100:.2f}",
            f"{estrutura_params_A['strike_call']*100:.2f}",
            f"{estrutura_params_A['barreira_ativacao']*100:.2f}",
            f"{estrutura_params_A['prejuizo_maximo']*100:.2f}",
            f"{estrutura_params_A['ganho_max_ativado']*100:.2f}",
            f"{estrutura_params_A['ganho_max_nao_ativado']*100:.2f}",
            f"{estrutura_params_A['dias_uteis']}",
            estrutura_params_A['data_vencimento'].strftime('%d-%m-%Y'),
        ],
        "Estrutura B": [
            ticker_B,
            f"R$ {estrutura_params_B['S0']:.2f}",
            f"{estrutura_params_B['strike_put']*100:.2f}",
            f"{estrutura_params_B['strike_call']*100:.2f}",
            f"{estrutura_params_B['barreira_ativacao']*100:.2f}",
            f"{estrutura_params_B['prejuizo_maximo']*100:.2f}",
            f"{estrutura_params_B['ganho_max_ativado']*100:.2f}",
            f"{estrutura_params_B['ganho_max_nao_ativado']*100:.2f}",
            f"{estrutura_params_B['dias_uteis']}",
            estrutura_params_B['data_vencimento'].strftime('%d-%m-%Y'),
        ],
    })
    print(params_table.to_string(index=False))
    
    # Métricas de retorno e risco
    print("\n" + "-"*80)
    print("MÉTRICAS DE RETORNO E RISCO")
    print("-"*80)
    
    metrics_table = pd.DataFrame({
        "Métrica": [
            "Retorno Esperado (%)",
            "Desvio Padrão (%)",
            "Sharpe Ratio",
            "Sortino Ratio",
            "Mínimo (%)",
            "Máximo (%)",
            "Mediana (%)",
        ],
        "Estrutura A": [
            f"{metrics['expected_return']['A']*100:.2f}",
            f"{metrics['std']['A']*100:.2f}",
            f"{metrics['sharpe_ratio']['A']:.3f}",
            f"{metrics['sortino_ratio']['A']:.3f}",
            f"{np.min(payoffs_A)*100:.2f}",
            f"{np.max(payoffs_A)*100:.2f}",
            f"{np.median(payoffs_A)*100:.2f}",
        ],
        "Estrutura B": [
            f"{metrics['expected_return']['B']*100:.2f}",
            f"{metrics['std']['B']*100:.2f}",
            f"{metrics['sharpe_ratio']['B']:.3f}",
            f"{metrics['sortino_ratio']['B']:.3f}",
            f"{np.min(payoffs_B)*100:.2f}",
            f"{np.max(payoffs_B)*100:.2f}",
            f"{np.median(payoffs_B)*100:.2f}",
        ],
        "Diferença (B - A)": [
            f"{(metrics['expected_return']['B'] - metrics['expected_return']['A'])*100:+.2f}",
            f"{(metrics['std']['B'] - metrics['std']['A'])*100:+.2f}",
            f"{metrics['sharpe_ratio']['B'] - metrics['sharpe_ratio']['A']:+.3f}",
            f"{metrics['sortino_ratio']['B'] - metrics['sortino_ratio']['A']:+.3f}",
            f"{(np.min(payoffs_B) - np.min(payoffs_A))*100:+.2f}",
            f"{(np.max(payoffs_B) - np.max(payoffs_A))*100:+.2f}",
            f"{(np.median(payoffs_B) - np.median(payoffs_A))*100:+.2f}",
        ],
    })
    print(metrics_table.to_string(index=False))
    
    # Probabilidades de cenários
    print("\n" + "-"*80)
    print("PROBABILIDADES DE CENÁRIOS")
    print("-"*80)
    
    prob_table = pd.DataFrame({
        "Cenário": [
            "Perda",
            "Ganho (sem barreira)",
            "Ganho (barreira ativada)",
            "Ganho Positivo (qualquer)",
            "Perda Máxima",
            "Ganho Máx. (Barreira Ativada)",
            "Ganho Máx. (Barreira NÃO Ativada)",
        ],
        "Estrutura A (%)": [
            f"{metrics['prob_perda']['A']*100:.2f}",
            f"{metrics['prob_ganho_sem_barreira']['A']*100:.2f}",
            f"{metrics['prob_ganho_com_barreira']['A']*100:.2f}",
            f"{metrics['prob_ganho_positivo']['A']*100:.2f}",
            f"{metrics['prob_perda_max']['A']*100:.2f}",
            f"{metrics['prob_ganho_max_ativado']['A']*100:.2f}",
            f"{metrics['prob_ganho_max_nao_ativado']['A']*100:.2f}",
        ],
        "Estrutura B (%)": [
            f"{metrics['prob_perda']['B']*100:.2f}",
            f"{metrics['prob_ganho_sem_barreira']['B']*100:.2f}",
            f"{metrics['prob_ganho_com_barreira']['B']*100:.2f}",
            f"{metrics['prob_ganho_positivo']['B']*100:.2f}",
            f"{metrics['prob_perda_max']['B']*100:.2f}",
            f"{metrics['prob_ganho_max_ativado']['B']*100:.2f}",
            f"{metrics['prob_ganho_max_nao_ativado']['B']*100:.2f}",
        ],
        "Diferença (B - A)": [
            f"{(metrics['prob_perda']['B'] - metrics['prob_perda']['A'])*100:+.2f}",
            f"{(metrics['prob_ganho_sem_barreira']['B'] - metrics['prob_ganho_sem_barreira']['A'])*100:+.2f}",
            f"{(metrics['prob_ganho_com_barreira']['B'] - metrics['prob_ganho_com_barreira']['A'])*100:+.2f}",
            f"{(metrics['prob_ganho_positivo']['B'] - metrics['prob_ganho_positivo']['A'])*100:+.2f}",
            f"{(metrics['prob_perda_max']['B'] - metrics['prob_perda_max']['A'])*100:+.2f}",
            f"{(metrics['prob_ganho_max_ativado']['B'] - metrics['prob_ganho_max_ativado']['A'])*100:+.2f}",
            f"{(metrics['prob_ganho_max_nao_ativado']['B'] - metrics['prob_ganho_max_nao_ativado']['A'])*100:+.2f}",
        ],
    })
    print(prob_table.to_string(index=False))
    
    # Métricas de risco
    print("\n" + "-"*80)
    print("MÉTRICAS DE RISCO")
    print("-"*80)
    
    risk_table = pd.DataFrame({
        "Métrica": [
            "VaR 5% (%)",
            "CVaR 5% (%)",
            "Percentil 5% (%)",
            "Percentil 25% (%)",
            "Percentil 75% (%)",
            "Percentil 95% (%)",
            "Ganho Esperado Condicional (%)",
        ],
        "Estrutura A": [
            f"{metrics['VaR_5']['A']*100:.2f}",
            f"{metrics['CVaR_5']['A']*100:.2f}",
            f"{metrics['percentis']['A'][5]*100:.2f}",
            f"{metrics['percentis']['A'][25]*100:.2f}",
            f"{metrics['percentis']['A'][75]*100:.2f}",
            f"{metrics['percentis']['A'][95]*100:.2f}",
            f"{metrics['ganho_esperado_condicional']['A']*100:.2f}",
        ],
        "Estrutura B": [
            f"{metrics['VaR_5']['B']*100:.2f}",
            f"{metrics['CVaR_5']['B']*100:.2f}",
            f"{metrics['percentis']['B'][5]*100:.2f}",
            f"{metrics['percentis']['B'][25]*100:.2f}",
            f"{metrics['percentis']['B'][75]*100:.2f}",
            f"{metrics['percentis']['B'][95]*100:.2f}",
            f"{metrics['ganho_esperado_condicional']['B']*100:.2f}",
        ],
        "Diferença (B - A)": [
            f"{(metrics['VaR_5']['B'] - metrics['VaR_5']['A'])*100:+.2f}",
            f"{(metrics['CVaR_5']['B'] - metrics['CVaR_5']['A'])*100:+.2f}",
            f"{(metrics['percentis']['B'][5] - metrics['percentis']['A'][5])*100:+.2f}",
            f"{(metrics['percentis']['B'][25] - metrics['percentis']['A'][25])*100:+.2f}",
            f"{(metrics['percentis']['B'][75] - metrics['percentis']['A'][75])*100:+.2f}",
            f"{(metrics['percentis']['B'][95] - metrics['percentis']['A'][95])*100:+.2f}",
            f"{(metrics['ganho_esperado_condicional']['B'] - metrics['ganho_esperado_condicional']['A'])*100:+.2f}",
        ],
    })
    print(risk_table.to_string(index=False))
    
    # Recomendação
    print("\n" + "-"*80)
    print("ANÁLISE E RECOMENDAÇÃO")
    print("-"*80)
    
    melhor_retorno = "A" if metrics['expected_return']['A'] > metrics['expected_return']['B'] else "B"
    melhor_sharpe = "A" if metrics['sharpe_ratio']['A'] > metrics['sharpe_ratio']['B'] else "B"
    menor_risco = "A" if metrics['std']['A'] < metrics['std']['B'] else "B"
    maior_prob_ganho = "A" if metrics['prob_ganho_positivo']['A'] > metrics['prob_ganho_positivo']['B'] else "B"
    
    print(f"✓ Melhor Retorno Esperado: Estrutura {melhor_retorno}")
    print(f"✓ Melhor Sharpe Ratio: Estrutura {melhor_sharpe}")
    print(f"✓ Menor Risco (Desvio Padrão): Estrutura {menor_risco}")
    print(f"✓ Maior Probabilidade de Ganho Positivo: Estrutura {maior_prob_ganho}")
    
    # Score composto simples
    score_A = (
        0.3 * metrics['expected_return']['A'] +
        0.2 * metrics['sharpe_ratio']['A'] +
        0.2 * metrics['prob_ganho_positivo']['A'] +
        0.15 * (-metrics['CVaR_5']['A']) +  # Negativo porque menor é melhor
        0.15 * metrics['ganho_esperado_condicional']['A']
    )
    score_B = (
        0.3 * metrics['expected_return']['B'] +
        0.2 * metrics['sharpe_ratio']['B'] +
        0.2 * metrics['prob_ganho_positivo']['B'] +
        0.15 * (-metrics['CVaR_5']['B']) +
        0.15 * metrics['ganho_esperado_condicional']['B']
    )
    
    melhor_score = "A" if score_A > score_B else "B"
    print(f"\n✓ Score Composto (ponderado): Estrutura {melhor_score} (A: {score_A:.4f}, B: {score_B:.4f})")
    
    print("\n" + "="*80 + "\n")


def plot_comparison(
    payoffs_A: np.ndarray,
    payoffs_B: np.ndarray,
    paths_A: np.ndarray,
    paths_B: np.ndarray,
    cenarios_A: np.ndarray,
    cenarios_B: np.ndarray,
    ticker_A: str,
    ticker_B: str,
    estrutura_params_A: Dict,
    estrutura_params_B: Dict,
    metrics: Dict,
) -> None:
    """Gera visualizações comparativas das duas estruturas."""
    
    # Figura principal com múltiplos subplots
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 1. Histogramas comparativos lado a lado
    ax1 = fig.add_subplot(gs[0, :])
    ax1.hist(payoffs_A * 100, bins=50, alpha=0.6, label='Estrutura A', color='steelblue', edgecolor='black')
    ax1.hist(payoffs_B * 100, bins=50, alpha=0.6, label='Estrutura B', color='orange', edgecolor='black')
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax1.axvline(x=metrics['expected_return']['A']*100, color='blue', linestyle='--', linewidth=2, label=f'A Média: {metrics["expected_return"]["A"]*100:.2f}%')
    ax1.axvline(x=metrics['expected_return']['B']*100, color='red', linestyle='--', linewidth=2, label=f'B Média: {metrics["expected_return"]["B"]*100:.2f}%')
    ax1.set_xlabel('Payoff (%)')
    ax1.set_ylabel('Frequência')
    ax1.set_title('Distribuição Comparativa de Payoffs', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Box plots comparativos
    ax2 = fig.add_subplot(gs[1, 0])
    bp = ax2.boxplot([payoffs_A * 100, payoffs_B * 100], labels=['Estrutura A', 'Estrutura B'], 
                     patch_artist=True)
    bp['boxes'][0].set_facecolor('steelblue')
    bp['boxes'][1].set_facecolor('orange')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax2.set_ylabel('Payoff (%)')
    ax2.set_title('Box Plot Comparativo', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. CDF Comparativa
    ax3 = fig.add_subplot(gs[1, 1])
    sorted_A = np.sort(payoffs_A)
    sorted_B = np.sort(payoffs_B)
    ax3.plot(sorted_A * 100, np.arange(len(sorted_A))/len(sorted_A), 
             label='Estrutura A', linewidth=2, color='steelblue')
    ax3.plot(sorted_B * 100, np.arange(len(sorted_B))/len(sorted_B), 
             label='Estrutura B', linewidth=2, color='orange')
    ax3.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax3.set_xlabel('Payoff (%)')
    ax3.set_ylabel('Probabilidade Cumulativa')
    ax3.set_title('Função de Distribuição Cumulativa (CDF)', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Scatter: Retorno vs Risco
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.scatter(metrics['std']['A']*100, metrics['expected_return']['A']*100, 
                s=200, label='Estrutura A', color='steelblue', alpha=0.7, edgecolors='black')
    ax4.scatter(metrics['std']['B']*100, metrics['expected_return']['B']*100, 
                s=200, label='Estrutura B', color='orange', alpha=0.7, edgecolors='black')
    ax4.set_xlabel('Risco (Desvio Padrão %)')
    ax4.set_ylabel('Retorno Esperado (%)')
    ax4.set_title('Retorno vs Risco', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Comparação de probabilidades de cenários
    ax5 = fig.add_subplot(gs[2, 1])
    cenarios_labels = ['Perda', 'Ganho\n(sem barreira)', 'Ganho\n(barreira ativada)']
    x = np.arange(len(cenarios_labels))
    width = 0.35
    
    prob_A = [
        metrics['prob_perda']['A']*100,
        metrics['prob_ganho_sem_barreira']['A']*100,
        metrics['prob_ganho_com_barreira']['A']*100,
    ]
    prob_B = [
        metrics['prob_perda']['B']*100,
        metrics['prob_ganho_sem_barreira']['B']*100,
        metrics['prob_ganho_com_barreira']['B']*100,
    ]
    
    ax5.bar(x - width/2, prob_A, width, label='Estrutura A', color='steelblue', alpha=0.7)
    ax5.bar(x + width/2, prob_B, width, label='Estrutura B', color='orange', alpha=0.7)
    ax5.set_ylabel('Probabilidade (%)')
    ax5.set_title('Probabilidades de Cenários', fontsize=12, fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels(cenarios_labels)
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle(f'Comparação de Estruturas COLLAR UI - {ticker_A} vs {ticker_B}', 
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.show()


def main() -> None:
    """Função principal que executa a comparação de duas estruturas."""
    ticker_A, estrutura_params_1, ticker_B, estrutura_params_2, n_caminhos = ask_user_inputs()
    
    print(f"\n{'='*80}")
    print("INICIANDO SIMULAÇÃO")
    print(f"{'='*80}")
    
    # Simulação Estrutura A
    print(f"\n{'='*80}")
    print(f"ESTRUTURA A - {ticker_A}")
    print(f"{'='*80}")
    S0_A = estrutura_params_1["S0"]
    dias_uteis_A = estrutura_params_1["dias_uteis"]
    print(f"Baixando dados históricos para {ticker_A}...")
    prices_A = get_price_series(ticker_A, dias_uteis_A)
    print(f"Gerando {n_caminhos} caminhos para {dias_uteis_A} dias úteis...")
    paths_A = generate_mbb_paths(prices_A, S0_A, dias_uteis_A, n_caminhos)
    print("Calculando payoffs...")
    payoffs_A, cenarios_A, stats_A = calculate_collar_ui_payoffs(paths_A, estrutura_params_1)
    
    # Simulação Estrutura B
    print(f"\n{'='*80}")
    print(f"ESTRUTURA B - {ticker_B}")
    print(f"{'='*80}")
    S0_B = estrutura_params_2["S0"]
    dias_uteis_B = estrutura_params_2["dias_uteis"]
    print(f"Baixando dados históricos para {ticker_B}...")
    prices_B = get_price_series(ticker_B, dias_uteis_B)
    print(f"Gerando {n_caminhos} caminhos para {dias_uteis_B} dias úteis...")
    paths_B = generate_mbb_paths(prices_B, S0_B, dias_uteis_B, n_caminhos)
    print("Calculando payoffs...")
    payoffs_B, cenarios_B, stats_B = calculate_collar_ui_payoffs(paths_B, estrutura_params_2)
    
    # Cálculo de métricas comparativas
    print(f"\n{'='*80}")
    print("CALCULANDO MÉTRICAS COMPARATIVAS")
    print(f"{'='*80}")
    metrics = calculate_comparison_metrics(
        payoffs_A, payoffs_B, cenarios_A, cenarios_B,
        estrutura_params_1, estrutura_params_2
    )
    
    # Relatório comparativo
    print_comparison_report(
        payoffs_A, payoffs_B, cenarios_A, cenarios_B,
        ticker_A, ticker_B, estrutura_params_1, estrutura_params_2, metrics
    )
    
    # Visualizações
    print("Gerando gráficos comparativos...")
    plot_comparison(
        payoffs_A, payoffs_B, paths_A, paths_B,
        cenarios_A, cenarios_B, ticker_A, ticker_B,
        estrutura_params_1, estrutura_params_2, metrics
    )


if __name__ == "__main__":
    main()
