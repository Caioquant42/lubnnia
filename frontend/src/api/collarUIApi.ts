import axios from 'axios';
import { apiBaseUrl, defaultHeaders, requestTimeout } from './config';

// Comparison types and functions
export interface CollarUIComparisonParams {
  ticker_A: string;
  S0_A: number;
  strike_put_pct_A: number;
  strike_call_pct_A: number;
  expiration_date_A: string; // DD-MM-YYYY format
  barrier_pct_A: number;
  ticker_B: string;
  S0_B: number;
  strike_put_pct_B: number;
  strike_call_pct_B: number;
  expiration_date_B: string; // DD-MM-YYYY format
  barrier_pct_B: number;
  n_bootstrap?: number;
}

export interface CollarUIComparisonStructure {
  ticker: string;
  params: {
    S0: number;
    strike_put: number;
    strike_call: number;
    data_vencimento: string;
    dias_uteis: number;
    barreira_ativacao: number;
    ganho_max_ativado: number;
    ganho_max_nao_ativado: number;
    prejuizo_maximo: number;
  };
  statistics: {
    n_perda: number;
    n_ganho_sem_barreira: number;
    n_ganho_com_barreira: number;
    pct_perda: number;
    pct_ganho_sem_barreira: number;
    pct_ganho_com_barreira: number;
    payoff_medio: number;
    payoff_mediano: number;
    payoff_std: number;
    payoff_min: number;
    payoff_max: number;
  };
  payoffs: number[];
  scenarios: number[];
  paths: number[][];
}

export interface CollarUIComparisonMetrics {
  expected_return: { A: number; B: number };
  std: { A: number; B: number };
  sharpe_ratio: { A: number; B: number };
  sortino_ratio: { A: number; B: number };
  prob_perda: { A: number; B: number };
  prob_ganho_sem_barreira: { A: number; B: number };
  prob_ganho_com_barreira: { A: number; B: number };
  prob_ganho_positivo: { A: number; B: number };
  ganho_esperado_condicional: { A: number; B: number };
  VaR_5: { A: number; B: number };
  CVaR_5: { A: number; B: number };
  percentis: {
    A: { [key: number]: number };
    B: { [key: number]: number };
  };
  prob_perda_max: { A: number; B: number };
  prob_ganho_max_ativado: { A: number; B: number };
  prob_ganho_max_nao_ativado: { A: number; B: number };
}

export interface CollarUIComparisonResponse {
  structure_A: CollarUIComparisonStructure;
  structure_B: CollarUIComparisonStructure;
  comparison_metrics: CollarUIComparisonMetrics;
  composite_scores: {
    A: number;
    B: number;
  };
  recommendation: 'A' | 'B';
}

export async function getCollarUIComparison(params: CollarUIComparisonParams) {
  const response = await axios.get<CollarUIComparisonResponse>(`${apiBaseUrl}/api/collar-ui/compare`, {
    headers: defaultHeaders,
    timeout: requestTimeout * 2, // Longer timeout for comparison
    params,
  });
  return response.data;
}

// Single view types and functions
export interface CollarUISingleParams {
  ticker: string;
  S0: number;
  strike_put_pct: number;
  strike_call_pct: number;
  expiration_date: string; // DD-MM-YYYY format
  barrier_pct: number;
  n_bootstrap?: number;
}

export interface CollarUISingleStructure {
  ticker: string;
  params: {
    S0: number;
    strike_put: number;
    strike_call: number;
    data_vencimento: string;
    dias_uteis: number;
    barreira_ativacao: number;
    ganho_max_ativado: number;
    ganho_max_nao_ativado: number;
    prejuizo_maximo: number;
  };
  statistics: {
    n_perda: number;
    n_ganho_sem_barreira: number;
    n_ganho_com_barreira: number;
    pct_perda: number;
    pct_ganho_sem_barreira: number;
    pct_ganho_com_barreira: number;
    payoff_medio: number;
    payoff_mediano: number;
    payoff_std: number;
    payoff_min: number;
    payoff_max: number;
  };
  payoffs: number[];
  scenarios: number[];
  paths: number[][];
  additional_metrics: {
    expected_return: number;
    std: number;
    sharpe_ratio: number;
    sortino_ratio: number;
    prob_ganho_positivo: number;
    ganho_esperado_condicional: number;
    VaR_5: number;
    CVaR_5: number;
    percentis: { [key: number]: number };
    prob_perda_max: number;
    prob_ganho_max_ativado: number;
    prob_ganho_max_nao_ativado: number;
  };
}

export interface CollarUISingleResponse {
  ticker: string;
  params: CollarUISingleStructure['params'];
  statistics: CollarUISingleStructure['statistics'];
  payoffs: number[];
  scenarios: number[];
  paths: number[][];
  additional_metrics: CollarUISingleStructure['additional_metrics'];
}

export async function getCollarUISingle(params: CollarUISingleParams) {
  const response = await axios.get<CollarUISingleResponse>(`${apiBaseUrl}/api/collar-ui/single`, {
    headers: defaultHeaders,
    timeout: requestTimeout * 2, // Longer timeout for single analysis
    params,
  });
  return response.data;
}


