from typing import Any, Dict, Tuple
from datetime import datetime
import numpy as np

from .mbb import MBBCore, DataGatherer


class CollarUICalculator:
    """
    Collar UI (Collar Up & In) calculator using Moving Block Bootstrap (MBB).

    Reimplementa a lógica dos notebooks MC_COLLAR_UI* substituindo whale_wallet
    por MBB (moving block bootstrap + Monte Carlo) para preservar dependência
    temporal dos retornos.
    """

    def __init__(self, n_bootstrap: int = 1000, iterations: int = 50000):
        self.n_bootstrap = n_bootstrap
        self.iterations = iterations
        self.mbb_core = MBBCore()
        self.data_gatherer = DataGatherer(use_monte_carlo_selection=False)

    def calculate_collar_ui_strategy(
        self,
        ticker: str,
        ttm: int,
        max_loss: float,
        threshold_percentage: float,
        limited_gain: float,
        s0_override: float = None,
        n_bootstrap: int = None,
        iterations: int = None,
    ) -> Dict[str, Any]:
        """
        Calcula a estratégia Collar Up & In com MBB.
        Args:
            ticker: ativo (ex: VALE3 ou VALE3.SA)
            ttm: dias úteis até vencimento
            max_loss: perda máxima (ex: -0.05 para -5%)
            threshold_percentage: barreira de knockout (ex: 0.1346 para 13.46%)
            limited_gain: ganho limitado (ex: 0.048 para 4.8%)
            s0_override: preço de referência opcional; caso None, usa último close
            n_bootstrap: sobrescreve padrão de amostras bootstrap
            iterations: sobrescreve padrão de iterações MC
        """
        nb = n_bootstrap or self.n_bootstrap
        iters = iterations or self.iterations

        ticker_sa = ticker if ticker.endswith(".SA") else f"{ticker}.SA"

        # 1) Dados históricos (ttm dias)
        hist = self.data_gatherer.get_data(
            asset_list=[ticker_sa],
            period=f"{max(ttm, 30)}d",  # garante mínimo de dados
            interval="1d",
            data_type="Close",
        )
        if hist.empty or ticker_sa not in hist.columns:
            raise ValueError(f"Nenhum dado histórico encontrado para {ticker}")

        prices = hist[ticker_sa].dropna()
        if prices.empty:
            raise ValueError(f"Nenhum preço válido para {ticker}")

        S0 = float(s0_override) if s0_override is not None else float(prices.iloc[-1])
        log_returns = prices.pct_change().dropna()
        if log_returns.empty:
            raise ValueError("Não foi possível calcular retornos históricos.")

        sample_size = min(ttm, len(log_returns))

        # 2) Moving Block Bootstrap
        bootstrap_samples = self.mbb_core.moving_block_bootstrap(
            log_returns,
            n_bootstrap=nb,
            sample_size=sample_size,
        )

        # 3) Monte Carlo usando amostras bootstrap
        final_prices = self.mbb_core.monte_carlo_simulation(
            S0,
            bootstrap_samples,
            iterations=iters,
        )

        # 4) Parâmetros da estrutura
        strike_call = S0 * (1 + threshold_percentage)
        threshold = strike_call  # mesma definição do notebook

        # 5) Payoffs e cenários
        payoffs, scenario_counts, scenarios = self.calculate_strategy_payoff(
            final_prices, S0, strike_call, threshold, max_loss, limited_gain
        )

        expected_value = float(np.mean(payoffs)) if len(payoffs) else 0.0
        percentiles = {
            "1%": float(np.percentile(payoffs, 1)),
            "5%": float(np.percentile(payoffs, 5)),
            "25%": float(np.percentile(payoffs, 25)),
            "50%": float(np.percentile(payoffs, 50)),
            "75%": float(np.percentile(payoffs, 75)),
            "95%": float(np.percentile(payoffs, 95)),
            "99%": float(np.percentile(payoffs, 99)),
        }

        total_paths = max(sum(scenario_counts.values()), 1)
        scenario_percentages = {
            k: (v / total_paths) * 100 for k, v in scenario_counts.items()
        }

        metadata = {
            "ticker": ticker,
            "S0": S0,
            "ttm": ttm,
            "barreira_knockout": strike_call,
            "perda_maxima": S0 * max_loss,
            "ganho_maximo": S0 * limited_gain,
            "spot_price": S0,
            "timestamp": datetime.utcnow().isoformat(),
            "n_bootstrap": nb,
            "iterations": iters,
            "sample_size": sample_size,
        }

        statistics = {
            "expected_value": expected_value,
            "mean_payoff": float(np.mean(payoffs)) if len(payoffs) else 0.0,
            "median_payoff": float(np.median(payoffs)) if len(payoffs) else 0.0,
            "std_payoff": float(np.std(payoffs)) if len(payoffs) else 0.0,
            "min_payoff": float(np.min(payoffs)) if len(payoffs) else 0.0,
            "max_payoff": float(np.max(payoffs)) if len(payoffs) else 0.0,
            "percentiles": percentiles,
        }

        response = {
            "metadata": metadata,
            "statistics": statistics,
            "scenarios": scenario_counts,
            "scenario_percentages": scenario_percentages,
            "payoff_distribution": payoffs.tolist(),
            "price_distribution": final_prices.tolist(),
        }

        return response

    def calculate_strategy_payoff(
        self,
        final_prices: np.ndarray,
        S0: float,
        strike_call: float,
        threshold: float,
        max_loss: float,
        limited_gain: float,
    ) -> Tuple[np.ndarray, Dict[str, int], np.ndarray]:
        """
        Calcula payoffs e cenários da estrutura Collar Up & In.
        Cenários:
            0: downside
            1: normal upside
            2: knockout scenario 2 (entre strike_call e threshold)
            3: knockout scenario 1 (acima de threshold)
        """
        if isinstance(final_prices, (int, float, np.number)):
            final_prices = np.array([final_prices])
        final_prices = np.array(final_prices, dtype=float)

        payoffs = np.zeros(len(final_prices))
        scenarios = np.zeros(len(final_prices), dtype=int)

        for i, final_price in enumerate(final_prices):
            if final_price <= S0:
                # Downside scenario with maximum loss
                payoffs[i] = max(final_price - S0, S0 * max_loss)
                scenarios[i] = 0
            elif final_price > threshold:
                # Knockout scenario 1: maximum gain
                payoffs[i] = S0 * limited_gain
                scenarios[i] = 3
            elif final_price > strike_call:
                # Knockout scenario 2: limited gain
                payoffs[i] = min(final_price - S0, S0 * limited_gain)
                scenarios[i] = 2
            else:
                # Normal upside scenario
                payoffs[i] = final_price - S0
                scenarios[i] = 1

        scenario_counts = {
            "downside": int(np.sum(scenarios == 0)),
            "normal_upside": int(np.sum(scenarios == 1)),
            "knockout_scenario2": int(np.sum(scenarios == 2)),
            "knockout_scenario1": int(np.sum(scenarios == 3)),
        }

        return payoffs, scenario_counts, scenarios


def get_collar_ui_analysis(
    ticker: str,
    ttm: int,
    max_loss: float,
    threshold_percentage: float,
    limited_gain: float,
    s0_override: float = None,
    n_bootstrap: int = 1000,
    iterations: int = 50000,
) -> Dict[str, Any]:
    """
    Função helper para uso direto (simples) sem instanciar a classe.
    """
    calculator = CollarUICalculator(n_bootstrap=n_bootstrap, iterations=iterations)
    return calculator.calculate_collar_ui_strategy(
        ticker=ticker,
        ttm=ttm,
        max_loss=max_loss,
        threshold_percentage=threshold_percentage,
        limited_gain=limited_gain,
        s0_override=s0_override,
        n_bootstrap=n_bootstrap,
        iterations=iterations,
    )


