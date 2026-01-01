"""
Collar UI Comparison Module

Compares two Collar UI structures using Moving Block Bootstrap (MBB).
Based on mbb_bootstrap_paths_comparison.py script.
"""

from typing import Dict, Tuple, Any
from datetime import datetime, timedelta
import numpy as np

from .mbb import MBBCore, DataGatherer


def business_days_between(start_date: datetime, end_date: datetime) -> int:
    """Calcula o número de dias úteis entre duas datas."""
    return int(np.busday_count(start_date.date(), end_date.date()))


class CollarUIComparison:
    """
    Compares two Collar UI structures using Moving Block Bootstrap.
    """

    def __init__(self, n_bootstrap: int = 1000):
        self.n_bootstrap = n_bootstrap
        self.mbb_core = MBBCore()
        self.data_gatherer = DataGatherer(use_monte_carlo_selection=False)

    def get_price_series(self, ticker: str, dias_uteis: int) -> np.ndarray:
        """Baixa a série de preços de fechamento do ativo usando DataGatherer."""
        # Calcula período necessário: pelo menos 3x o horizonte ou horizonte + 20 dias
        periodo_dias = max(dias_uteis * 3, dias_uteis + 20)
        
        ticker_sa = ticker if ticker.endswith(".SA") else f"{ticker}.SA"
        
        # Se o período for muito longo (> 2 anos), usa start_date/end_date
        if periodo_dias > 500:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=int(periodo_dias * 1.5))
            df = self.data_gatherer.get_data(
                asset_list=[ticker_sa],
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
        else:
            period_str = f"{periodo_dias}d"
            df = self.data_gatherer.get_data(asset_list=[ticker_sa], period=period_str)
        
        if df.empty or ticker_sa not in df.columns:
            raise ValueError(f"Não foi possível baixar dados para o ativo {ticker}.")
        
        col_name = df.columns[0]
        prices = df[col_name].values.astype(float)
        
        # Verifica se há dados suficientes
        if len(prices) < dias_uteis:
            if len(prices) < 20:
                raise ValueError(
                    f"ERRO: Número de observações ({len(prices)}) é muito pequeno. "
                    f"Necessário pelo menos {dias_uteis} dias úteis."
                )
        
        return prices

    def generate_mbb_paths(
        self,
        prices: np.ndarray,
        S0: float,
        dias_uteis: int,
        n_caminhos: int,
    ) -> np.ndarray:
        """Gera caminhos de preço usando Moving Block Bootstrap (MBB)."""
        # Retornos logarítmicos: log(P_t / P_{t-1}) = log(P_t) - log(P_{t-1})
        returns = np.diff(np.log(prices))
        
        bootstrap_samples = self.mbb_core.moving_block_bootstrap(
            returns,
            n_bootstrap=n_caminhos,
            sample_size=dias_uteis,
        )
        
        # Constrói os caminhos de preço usando retornos logarítmicos: P_t = P_0 * exp(sum(log_returns))
        paths_sem_S0 = S0 * np.exp(np.cumsum(bootstrap_samples, axis=1))
        paths = np.zeros((n_caminhos, dias_uteis + 1), dtype=float)
        paths[:, 0] = S0
        paths[:, 1:] = paths_sem_S0
        
        return paths

    def calculate_collar_ui_payoffs(
        self,
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
            "n_perda": int(np.sum(cenarios == 0)),
            "n_ganho_sem_barreira": int(np.sum(cenarios == 1)),
            "n_ganho_com_barreira": int(np.sum(cenarios == 2)),
            "pct_perda": float(np.sum(cenarios == 0) / n_caminhos * 100),
            "pct_ganho_sem_barreira": float(np.sum(cenarios == 1) / n_caminhos * 100),
            "pct_ganho_com_barreira": float(np.sum(cenarios == 2) / n_caminhos * 100),
            "payoff_medio": float(np.mean(payoffs)),
            "payoff_mediano": float(np.median(payoffs)),
            "payoff_std": float(np.std(payoffs)),
            "payoff_min": float(np.min(payoffs)),
            "payoff_max": float(np.max(payoffs)),
        }
        
        return payoffs, cenarios, stats

    def calculate_comparison_metrics(
        self,
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
        expected_return_A = float(np.mean(payoffs_A))
        expected_return_B = float(np.mean(payoffs_B))
        std_A = float(np.std(payoffs_A))
        std_B = float(np.std(payoffs_B))
        
        # Sharpe Ratio (assumindo taxa livre de risco = 0)
        sharpe_A = float(expected_return_A / std_A) if std_A > 0 else 0.0
        sharpe_B = float(expected_return_B / std_B) if std_B > 0 else 0.0
        
        # Sortino Ratio (volatilidade negativa)
        downside_std_A = float(np.std(payoffs_A[payoffs_A < 0])) if np.any(payoffs_A < 0) else 0.0
        downside_std_B = float(np.std(payoffs_B[payoffs_B < 0])) if np.any(payoffs_B < 0) else 0.0
        sortino_A = float(expected_return_A / downside_std_A) if downside_std_A > 0 else 0.0
        sortino_B = float(expected_return_B / downside_std_B) if downside_std_B > 0 else 0.0
        
        # Probabilidades de cenários
        prob_perda_A = float(np.sum(cenarios_A == 0) / len(cenarios_A))
        prob_perda_B = float(np.sum(cenarios_B == 0) / len(cenarios_B))
        prob_ganho_sem_barreira_A = float(np.sum(cenarios_A == 1) / len(cenarios_A))
        prob_ganho_sem_barreira_B = float(np.sum(cenarios_B == 1) / len(cenarios_B))
        prob_ganho_com_barreira_A = float(np.sum(cenarios_A == 2) / len(cenarios_A))
        prob_ganho_com_barreira_B = float(np.sum(cenarios_B == 2) / len(cenarios_B))
        
        # Probabilidade de ganho positivo
        prob_ganho_positivo_A = float(np.sum(payoffs_A > 0) / len(payoffs_A))
        prob_ganho_positivo_B = float(np.sum(payoffs_B > 0) / len(payoffs_B))
        
        # Ganho esperado condicional (dado que há ganho)
        ganho_esperado_condicional_A = float(np.mean(payoffs_A[payoffs_A > 0])) if np.any(payoffs_A > 0) else 0.0
        ganho_esperado_condicional_B = float(np.mean(payoffs_B[payoffs_B > 0])) if np.any(payoffs_B > 0) else 0.0
        
        # Value at Risk (VaR) e Conditional VaR (CVaR)
        VaR_5_A = float(np.percentile(payoffs_A, 5))
        VaR_5_B = float(np.percentile(payoffs_B, 5))
        CVaR_5_A = float(np.mean(payoffs_A[payoffs_A <= VaR_5_A])) if np.any(payoffs_A <= VaR_5_A) else VaR_5_A
        CVaR_5_B = float(np.mean(payoffs_B[payoffs_B <= VaR_5_B])) if np.any(payoffs_B <= VaR_5_B) else VaR_5_B
        
        # Percentis
        percentis = [5, 25, 50, 75, 95]
        percentis_A = {p: float(np.percentile(payoffs_A, p)) for p in percentis}
        percentis_B = {p: float(np.percentile(payoffs_B, p)) for p in percentis}
        
        # Probabilidade de perda máxima
        prob_perda_max_A = float(np.sum(payoffs_A <= -estrutura_params_A['prejuizo_maximo']) / len(payoffs_A))
        prob_perda_max_B = float(np.sum(payoffs_B <= -estrutura_params_B['prejuizo_maximo']) / len(payoffs_B))
        
        # Probabilidade de atingir ganho máximo
        prob_ganho_max_ativado_A = float(np.sum(payoffs_A >= estrutura_params_A['ganho_max_ativado']) / len(payoffs_A))
        prob_ganho_max_ativado_B = float(np.sum(payoffs_B >= estrutura_params_B['ganho_max_ativado']) / len(payoffs_B))
        prob_ganho_max_nao_ativado_A = float(
            np.sum((payoffs_A >= estrutura_params_A['ganho_max_nao_ativado']) & (cenarios_A == 1)) / len(payoffs_A)
        )
        prob_ganho_max_nao_ativado_B = float(
            np.sum((payoffs_B >= estrutura_params_B['ganho_max_nao_ativado']) & (cenarios_B == 1)) / len(payoffs_B)
        )
        
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

    def compare_structures(
        self,
        ticker_A: str,
        estrutura_params_A: Dict,
        ticker_B: str,
        estrutura_params_B: Dict,
        n_caminhos: int,
    ) -> Dict[str, Any]:
        """
        Compara duas estruturas COLLAR UI.
        
        Args:
            ticker_A: Ticker do ativo da estrutura A
            estrutura_params_A: Parâmetros da estrutura A (S0, strike_put, strike_call, etc.)
            ticker_B: Ticker do ativo da estrutura B
            estrutura_params_B: Parâmetros da estrutura B
            n_caminhos: Número de caminhos de bootstrap
        
        Returns:
            Dict com todos os dados de comparação
        """
        # Simulação Estrutura A
        S0_A = estrutura_params_A["S0"]
        dias_uteis_A = estrutura_params_A["dias_uteis"]
        prices_A = self.get_price_series(ticker_A, dias_uteis_A)
        paths_A = self.generate_mbb_paths(prices_A, S0_A, dias_uteis_A, n_caminhos)
        payoffs_A, cenarios_A, stats_A = self.calculate_collar_ui_payoffs(paths_A, estrutura_params_A)
        
        # Simulação Estrutura B
        S0_B = estrutura_params_B["S0"]
        dias_uteis_B = estrutura_params_B["dias_uteis"]
        prices_B = self.get_price_series(ticker_B, dias_uteis_B)
        paths_B = self.generate_mbb_paths(prices_B, S0_B, dias_uteis_B, n_caminhos)
        payoffs_B, cenarios_B, stats_B = self.calculate_collar_ui_payoffs(paths_B, estrutura_params_B)
        
        # Cálculo de métricas comparativas
        metrics = self.calculate_comparison_metrics(
            payoffs_A, payoffs_B, cenarios_A, cenarios_B,
            estrutura_params_A, estrutura_params_B
        )
        
        # Calcular score composto
        score_A = (
            0.3 * metrics['expected_return']['A'] +
            0.2 * metrics['sharpe_ratio']['A'] +
            0.2 * metrics['prob_ganho_positivo']['A'] +
            0.15 * (-metrics['CVaR_5']['A']) +
            0.15 * metrics['ganho_esperado_condicional']['A']
        )
        score_B = (
            0.3 * metrics['expected_return']['B'] +
            0.2 * metrics['sharpe_ratio']['B'] +
            0.2 * metrics['prob_ganho_positivo']['B'] +
            0.15 * (-metrics['CVaR_5']['B']) +
            0.15 * metrics['ganho_esperado_condicional']['B']
        )
        
        return {
            "structure_A": {
                "ticker": ticker_A,
                "params": estrutura_params_A,
                "statistics": stats_A,
                "payoffs": payoffs_A.tolist(),
                "scenarios": cenarios_A.tolist(),
                "paths": paths_A.tolist(),
            },
            "structure_B": {
                "ticker": ticker_B,
                "params": estrutura_params_B,
                "statistics": stats_B,
                "payoffs": payoffs_B.tolist(),
                "scenarios": cenarios_B.tolist(),
                "paths": paths_B.tolist(),
            },
            "comparison_metrics": metrics,
            "composite_scores": {
                "A": float(score_A),
                "B": float(score_B),
            },
            "recommendation": "A" if score_A > score_B else "B",
        }


def get_collar_ui_comparison(
    ticker_A: str,
    S0_A: float,
    strike_put_pct_A: float,
    strike_call_pct_A: float,
    expiration_date_A: str,
    barrier_pct_A: float,
    ticker_B: str,
    S0_B: float,
    strike_put_pct_B: float,
    strike_call_pct_B: float,
    expiration_date_B: str,
    barrier_pct_B: float,
    n_bootstrap: int = 1000,
) -> Dict[str, Any]:
    """
    Função helper para comparação de duas estruturas COLLAR UI.
    
    Args:
        ticker_A: Ticker do ativo A
        S0_A: Preço inicial do ativo A
        strike_put_pct_A: Strike Put em % do S0 (ex: 90.0 para 90%)
        strike_call_pct_A: Strike Call em % do S0 (ex: 107.5 para 107.5%)
        expiration_date_A: Data de vencimento (DD-MM-YYYY)
        barrier_pct_A: Barreira de ativação Up&In em % do S0 (ex: 144.0 para 144%)
        ticker_B: Ticker do ativo B
        S0_B: Preço inicial do ativo B
        strike_put_pct_B: Strike Put em % do S0 para B
        strike_call_pct_B: Strike Call em % do S0 para B
        expiration_date_B: Data de vencimento para B (DD-MM-YYYY)
        barrier_pct_B: Barreira de ativação para B em % do S0
        n_bootstrap: Número de caminhos de bootstrap
    
    Returns:
        Dict com dados de comparação
    """
    # Parse expiration dates
    data_venc_A = datetime.strptime(expiration_date_A, "%d-%m-%Y")
    data_venc_B = datetime.strptime(expiration_date_B, "%d-%m-%Y")
    data_atual = datetime.now()
    
    if data_venc_A <= data_atual or data_venc_B <= data_atual:
        raise ValueError("Data de vencimento deve ser futura.")
    
    # Calcula dias úteis
    dias_uteis_A = business_days_between(data_atual, data_venc_A)
    dias_uteis_B = business_days_between(data_atual, data_venc_B)
    
    if dias_uteis_A <= 0 or dias_uteis_B <= 0:
        raise ValueError("Data de vencimento muito próxima ou no passado.")
    
    # Converte percentuais para decimais
    strike_put_A = strike_put_pct_A / 100.0
    strike_call_A = strike_call_pct_A / 100.0
    barreira_ativacao_A = barrier_pct_A / 100.0
    
    strike_put_B = strike_put_pct_B / 100.0
    strike_call_B = strike_call_pct_B / 100.0
    barreira_ativacao_B = barrier_pct_B / 100.0
    
    # Calcula ganhos máximos
    ganho_max_ativado_A = strike_call_A - 1.0
    ganho_max_nao_ativado_A = barreira_ativacao_A - 1.0 - 0.0001
    prejuizo_maximo_A = 1.0 - strike_put_A
    
    ganho_max_ativado_B = strike_call_B - 1.0
    ganho_max_nao_ativado_B = barreira_ativacao_B - 1.0 - 0.0001
    prejuizo_maximo_B = 1.0 - strike_put_B
    
    estrutura_params_A = {
        "S0": S0_A,
        "strike_put": strike_put_A,
        "strike_call": strike_call_A,
        "data_vencimento": data_venc_A.isoformat(),
        "dias_uteis": dias_uteis_A,
        "barreira_ativacao": barreira_ativacao_A,
        "ganho_max_ativado": ganho_max_ativado_A,
        "ganho_max_nao_ativado": ganho_max_nao_ativado_A,
        "prejuizo_maximo": prejuizo_maximo_A,
    }
    
    estrutura_params_B = {
        "S0": S0_B,
        "strike_put": strike_put_B,
        "strike_call": strike_call_B,
        "data_vencimento": data_venc_B.isoformat(),
        "dias_uteis": dias_uteis_B,
        "barreira_ativacao": barreira_ativacao_B,
        "ganho_max_ativado": ganho_max_ativado_B,
        "ganho_max_nao_ativado": ganho_max_nao_ativado_B,
        "prejuizo_maximo": prejuizo_maximo_B,
    }
    
    comparator = CollarUIComparison(n_bootstrap=n_bootstrap)
    return comparator.compare_structures(
        ticker_A, estrutura_params_A,
        ticker_B, estrutura_params_B,
        n_bootstrap
    )

