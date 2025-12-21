import axios from 'axios';
import { apiBaseUrl, defaultHeaders, requestTimeout } from './config';

export interface CollarUIParameters {
  ticker: string;
  S0?: number;
  ttm: number;
  max_loss: number;
  threshold_percentage: number;
  limited_gain: number;
  n_bootstrap?: number;
  iterations?: number;
}

export interface CollarUIMetadata {
  ticker: string;
  S0: number;
  ttm: number;
  barreira_knockout: number;
  perda_maxima: number;
  ganho_maximo: number;
  spot_price: number;
  timestamp: string;
  n_bootstrap: number;
  iterations: number;
  sample_size: number;
}

export interface CollarUIStatistics {
  expected_value: number;
  mean_payoff: number;
  median_payoff: number;
  std_payoff: number;
  min_payoff: number;
  max_payoff: number;
  percentiles: Record<string, number>;
}

export interface CollarUIScenarios {
  downside: number;
  normal_upside: number;
  knockout_scenario2: number;
  knockout_scenario1: number;
}

export interface CollarUIResponse {
  metadata: CollarUIMetadata;
  statistics: CollarUIStatistics;
  scenarios: CollarUIScenarios;
  scenario_percentages: Record<string, number>;
  payoff_distribution: number[];
  price_distribution: number[];
}

export async function getCollarUIData(params: CollarUIParameters) {
  const response = await axios.get<CollarUIResponse>(`${apiBaseUrl}/api/collar-ui`, {
    headers: defaultHeaders,
    timeout: requestTimeout,
    params,
  });
  return response.data;
}


