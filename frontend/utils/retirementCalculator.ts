/**
 * Retirement planning calculation utilities
 */

import { RetirementParams, RetirementResults, RetirementDataPoint } from '@/types/retirement';

/**
 * Calculate the amount needed at retirement to cover the retirement period with anticipated withdrawals
 * 
 * @param A Annual retirement income (R$)
 * @param r Distribution phase interest rate (decimal)
 * @param m Distribution phase duration (years)
 * @returns Capital needed at start of retirement
 */
export function calculateNeededCapital(A: number, r: number, m: number): number {
  // Calculate needed capital with anticipated withdrawals
  // Each withdrawal happens at the BEGINNING of the period
  let necessary_capital = A;
  
  // Work backwards from the last period to the first
  for (let year = 0; year < m - 1; year++) {
    necessary_capital = A + necessary_capital / (1 + r);
  }
  
  return necessary_capital;
}

/**
 * Calculate exact investment fraction of salary needed to reach retirement goal
 * 
 * @param A Annual retirement income desired (R$)
 * @param i Accumulation phase interest rate (decimal)
 * @param r Distribution phase interest rate (decimal)
 * @param sal Annual salary (R$)
 * @param x0 Current age (years)
 * @param x1 Retirement age (years)
 * @param xOmega Maximum age to consider (years)
 * @returns Fraction of annual salary needed to invest
 */
export function calculateExactInvestmentFraction(
  A: number, 
  i: number, 
  r: number, 
  sal: number, 
  x0: number, 
  x1: number, 
  xOmega: number
): number {
  const n = x1 - x0; // Accumulation phase duration
  const m = xOmega - x1; // Distribution phase duration
  
  // First, calculate the capital needed to reach max age exactly
  // using the method with anticipated withdrawals
  const needed_capital = calculateNeededCapital(A, r, m);
  
  // Then, calculate the annual contribution needed to reach this capital
  const needed_contribution = needed_capital * i / ((1 + i) ** n - 1);
  
  // Calculate the fraction of salary
  const k = needed_contribution / sal;
  
  return k;
}

/**
 * Generate retirement calculation results based on input parameters
 * 
 * @param params Retirement planning parameters
 * @returns Complete retirement calculation results
 */
export function calculateRetirementPlan(params: RetirementParams): RetirementResults {
  // Destructure parameters
  const { 
    salary, 
    current_age, 
    retirement_age, 
    max_age,
    retirement_income, 
    accumulation_rate, 
    distribution_rate
  } = params;
  
  // Calculate years for each phase
  const accumulation_years = retirement_age - current_age;
  const distribution_years = max_age - retirement_age;
  
  // Calculate investment fraction if not provided
  const investment_fraction = params.investment_fraction || 
    calculateExactInvestmentFraction(
      retirement_income,
      accumulation_rate,
      distribution_rate,
      salary,
      current_age,
      retirement_age,
      max_age
    );
  
  // Calculate annual investment amount
  const annual_contribution = investment_fraction * salary;
  
  // Initialize array to store chart data
  const chartData: RetirementDataPoint[] = [];
  
  // Calculate accumulation phase values
  let current_value = params.initial_capital || 0;
  let total_contributed = 0;
  
  for (let year = 0; year <= accumulation_years; year++) {
    const age = current_age + year;
    
    // Add current state to chart data
    chartData.push({
      age,
      value: current_value,
      phase: 'accumulation',
      contribution: year < accumulation_years ? annual_contribution : 0
    });
    
    // Update for next year (if not the last year of accumulation)
    if (year < accumulation_years) {
      current_value = current_value * (1 + accumulation_rate) + annual_contribution;
      total_contributed += annual_contribution;
    }
  }
  
  // Store final accumulation value
  const final_accumulation = current_value;
  
  // Calculate distribution phase values
  let remaining_value = final_accumulation;
  let depletion_age: number | null = null;
  
  for (let year = 0; year <= distribution_years; year++) {
    const age = retirement_age + year;
    
    // For the retirement age (year=0), update the existing data point instead of adding a new one
    if (year === 0) {
      // Find the retirement age point (the last point in the chartData array)
      const retirementPoint = chartData[chartData.length - 1];
      
      // This point is both the end of accumulation and start of distribution
      // Add withdrawal information without changing the phase
      if (retirementPoint) {
        retirementPoint.withdrawal = retirement_income;
        // Keep the phase as 'accumulation' since it's the end of that phase
      }
    } else {
      // Add current state to chart data for subsequent years
      chartData.push({
        age,
        value: remaining_value,
        phase: 'distribution',
        withdrawal: year < distribution_years ? retirement_income : 0
      });
    }
    
    // Update for next year (if not the last year)
    if (year < distribution_years) {
      // First withdraw, then grow remaining amount
      remaining_value = (remaining_value - retirement_income) * (1 + distribution_rate);
      
      // Check if funds are depleted
      if (remaining_value <= 0 && depletion_age === null) {
        depletion_age = age + 1; // Age when funds run out
        remaining_value = 0;
      }
    }
  }
  
  // Return complete results
  return {
    chartData,
    investment_fraction,
    final_accumulation,
    total_contributed,
    investment_returns: final_accumulation - total_contributed,
    distribution_ending_balance: remaining_value,
    depletion_age,
    params
  };
}