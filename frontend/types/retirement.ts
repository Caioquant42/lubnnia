/**
 * Types for retirement planning functionality
 */

/**
 * Retirement planning parameters
 */
export interface RetirementParams {
  /**
   * Annual income (R$)
   */
  salary: number;
  
  /**
   * Current age (years)
   */
  current_age: number;
  
  /**
   * Retirement age (years)
   */
  retirement_age: number;
  
  /**
   * Maximum age to consider (years)
   */
  max_age: number;
  
  /**
   * Annual retirement income desired (R$)
   */
  retirement_income: number;
  
  /**
   * Annual interest rate during accumulation phase (decimal)
   */
  accumulation_rate: number;
  
  /**
   * Annual interest rate during distribution phase (decimal)
   */
  distribution_rate: number;
  
  /**
   * Fraction of salary to invest annually (decimal)
   */
  investment_fraction?: number;
  
  /**
   * Initial capital at current age (R$)
   */
  initial_capital?: number;
}

/**
 * Data for a single point in the retirement chart
 */
export interface RetirementDataPoint {
  age: number;
  value: number;
  phase: 'accumulation' | 'distribution';
  contribution?: number;
  withdrawal?: number;
}

/**
 * Results of retirement calculation
 */
export interface RetirementResults {
  // Chart data
  chartData: RetirementDataPoint[];
  
  // Calculated values
  investment_fraction: number;
  final_accumulation: number;
  total_contributed: number;
  investment_returns: number;
  distribution_ending_balance: number;
  depletion_age: number | null;
  
  // Input parameters (for reference)
  params: RetirementParams;
}