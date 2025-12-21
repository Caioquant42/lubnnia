import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler, MinMaxScaler

class OptionCalculator:
    def __init__(self, option_df: pd.DataFrame, type: str):
        self.option_df = option_df
        self.type = type

    def _bound_finder(self, x_bound, x_max,x_min):
        self.x_value = (x_bound*(x_max - x_min)) + x_min  
        return self.x_value 

    def filter_option(self, lower_bound, upper_bound):
        if self.type == 'call':
            max_strike_call = self.option_df['Strike'].max()
            min_strike_call = self.option_df['Strike'].min()
            lower_strike_call = self._bound_finder(x_bound=lower_bound, x_max=max_strike_call, x_min=min_strike_call)
            upper_strike_call = self._bound_finder(x_bound=upper_bound, x_max=max_strike_call, x_min=min_strike_call)
            self.filtered_call_df_pro = self.option_df[(self.option_df['Strike'] >= lower_strike_call) & (self.option_df['Strike'] <= upper_strike_call)]
            return self.filtered_call_df_pro
        elif self.type == 'put':
            max_strike_put = self.option_df['Strike'].max()
            min_strike_put = self.option_df['Strike'].min()
            lower_strike_put = self._bound_finder(x_bound=lower_bound, x_max=max_strike_put, x_min=min_strike_put)
            upper_strike_put = self._bound_finder(x_bound=upper_bound, x_max=max_strike_put, x_min=min_strike_put)
            self.filtered_put_df_pro = self.option_df[(self.option_df['Strike'] >= lower_strike_put) & (self.option_df['Strike'] <= upper_strike_put)]
            return self.filtered_put_df_pro
        else:
            max_strike = self.option_df['Strike'].max()
            min_strike = self.option_df['Strike'].min()
            lower_strike = self._bound_finder(x_bound=lower_bound, x_max=max_strike, x_min=min_strike)
            upper_strike = self._bound_finder(x_bound=upper_bound, x_max=max_strike, x_min=min_strike)
            self.filtered_df = self.option_df[(self.option_df['Strike'] >= lower_strike) & (self.option_df['Strike'] <= upper_strike)]
            return self.filtered_df


        

    def interpolate_strike(self, arrivals, method: str):
        arrivals = np.sort(arrivals)
        pop_column = 'POP-' + method
        ecdf_final_values = np.arange(1, len(arrivals) + 1) / len(arrivals)  # Probability of exercise of PUTS
        sf_final_values = 1 - ecdf_final_values  # Probability of exercise of Calls
        
        # Use vectorized operations for better performance
        strike_prices = self.option_df['Strike'].values
        
        if self.type == 'call':
            interpolated_values = np.interp(strike_prices, arrivals, sf_final_values)
        elif self.type == 'put':
            interpolated_values = np.interp(strike_prices, arrivals, ecdf_final_values)
        
        self.option_df[pop_column] = interpolated_values
        return self.option_df        
        

    def _normalize_volume(self):
        # Z-score Normalization
        scaler = StandardScaler()
        volume_data = self.option_df['Volume'].values.reshape(-1, 1)
        volume_data_normalized = scaler.fit_transform(volume_data)
        self.option_df['Normalized Volume'] = volume_data_normalized.flatten()
        return self.option_df
    
    def _bid_ask_spread(self):
        self.option_df['Spread'] = self.option_df['Of. Compra'] - self.option_df['Of. Venda']
        return self.option_df
    
    def basic_calculations(self):
        self._normalize_volume()
        self._bid_ask_spread()

    def calculate_d1_d2_prob(self, spot_price, strike_price, time_to_maturity, risk_free_rate, volatility):
        """
        Calculate d1, d2, and the probability of exercise for the Black-Scholes formula.

        Parameters:
        - option_type: 'call' or 'put'
        - spot_price: current stock price
        - strike_price: option's strike price
        - time_to_maturity: time until option expiration (in years)
        - risk_free_rate: risk-free interest rate (annualized)
        - volatility: annualized volatility of the underlying stock

        Returns:
        - d1: d1 parameter of the Black-Scholes formula
        - d2: d2 parameter of the Black-Scholes formula
        - prob_exercise: probability of exercise for the option
        """
        d1 = (np.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity) / (volatility * np.sqrt(time_to_maturity))
        d2 = d1 - volatility * np.sqrt(time_to_maturity)
        print(d2)
        
        if self.type == 'call':
            prob_exercise = norm.cdf(d2)
            print(prob_exercise)
        elif self.type == 'put':
            prob_exercise = norm.cdf(-d2)
        else:
            raise ValueError("Invalid option type. Use 'call' or 'put'.")
            
        return prob_exercise

class OptionValuation:
    def __init__(self, S0, option_df: pd.DataFrame, option_type:str):
        self.S0 = S0
        self.option_df = option_df
        self.option_type = option_type

    def _calc_moneyness(self, S0: float, strike: np.ndarray) -> np.ndarray:
        return S0 / strike
        
    def _add_moneyness(self, S0: float, option_df: pd.DataFrame) -> pd.DataFrame:
        if self.type == 'call':
            #Calls
            option_df['Moneyness'] = self._calc_moneyness(S0, option_df['Strike']).values
        elif self.type == 'put':
            #Puts
            option_df['Moneyness'] = 1/self._calc_moneyness(S0, option_df['Strike']).values
        return option_df
    def _normalize_volume(self):
        # Z-score Normalization
        scaler = StandardScaler()
        volume_data = self.option_df['Volume'].values.reshape(-1, 1)
        volume_data_normalized = scaler.fit_transform(volume_data)
        self.option_df['Normalized Volume'] = volume_data_normalized.flatten()
        return self.option_df
    
    def _bid_ask_spread(self):
        self.option_df['Spread'] = self.option_df['Of. Compra'] - self.option_df['Of. Venda']
        return self.option_df
    def basic_calculations(self):
        self._normalize_volume()
        self._bid_ask_spread()
        
    def MC_Price(self,all_simulations_data,r: float, T: float):
        self.basic_calculations()
        if self.option_type == 'call':
            MC_call_prices_df = pd.DataFrame(columns=['Strike', 'MC_Call_Price'])                
            sorted_call_strike = self.option_df['Strike']
            for strike_price in sorted_call_strike:
                # Calculate the call option price for the current strike
                MC_call_price = MC_call_option_price(strike_price, all_simulations_data, r, T)
                #print(MC_call_price)        
                # Append the result to the DataFrame
                row = pd.DataFrame({'Strike': [strike_price], 'MC_Call_Price': [MC_call_price]})
                MC_call_prices_df = pd.concat([MC_call_prices_df, row], ignore_index=True)

            # Reset index of MC_call_prices_df
            MC_call_prices_df.reset_index(drop=True, inplace=True)

            # Merge MC_call_prices_df with call_df based on 'Strike' column
            self.option_df = pd.merge(self.option_df, MC_call_prices_df)

            self.option_df['Último'] = pd.to_numeric(self.option_df['Último'], errors='coerce')
            self.option_df['ABS_Price_Diff'] = abs(self.option_df['Último'] - self.option_df['MC_Call_Price'])
            self.option_df['MC_Ratio'] = self.option_df['Último'] / self.option_df['MC_Call_Price']
            self.option_volatility()
            print(self.option_df.columns)
            print(self.option_df)
            return self.option_df               
        
        
        elif self.option_type == 'put':
            MC_put_prices_df = pd.DataFrame(columns=['Strike', 'MC_Put_Price'])
            sorted_put_strike = self.option_df['Strike']
            for strike_price in sorted_put_strike:
                # Calculate the put option price for the current strike
                MC_put_price = MC_put_option_price(strike_price, all_simulations_data, r, T)
                # Append the result to the DataFrame
                put_row = pd.DataFrame({'Strike': [strike_price], 'MC_Put_Price': [MC_put_price]})
                # Concatenate the new row
                MC_put_prices_df = pd.concat([MC_put_prices_df, put_row], ignore_index=True)

            # Reset index of MC_call_prices_df
            MC_put_prices_df.reset_index(drop=True, inplace=True)

            # Merge MC_call_prices_df with call_df based on 'Strike' column
            self.option_df = pd.merge(self.option_df, MC_put_prices_df)

            self.option_df['Último'] = pd.to_numeric(self.option_df['Último'], errors='coerce')
            self.option_df['ABS_Price_Diff'] = abs(self.option_df['Último'] - self.option_df['MC_Put_Price'])
            self.option_df['MC_Ratio'] = self.option_df['Último'] / self.option_df['MC_Put_Price']
            self.option_volatility()
            print(self.option_df.columns)
            print(self.option_df)
            return self.option_df   
        
        
    def leverage(self):    
        option_leverage = self.option_df['Delta']*(self.S0/self.option_df['Último'])
        return option_leverage

    def option_volatility(self):
        option_leverage = self.leverage()
        option_volatility = (self.option_df['Volt. Implícita']*option_leverage)
        self.option_df['Option Volatility'] = option_volatility
        self.option_df['Leverage'] = option_leverage
        return self.option_df

    def delta_ratio(self):
        if self.option_type =='call':            
            delta_difference = abs(self.option_df['Delta'] - self.option_df['SF'])
            self.option_df['Delta Difference'] = delta_difference
            delta_ratio = abs(self.option_df['Delta'] / self.option_df['SF'])
            self.option_df['Delta Ratio'] = delta_ratio
            return self.option_df
        elif self.option_type == 'put':
            delta_difference = abs(self.option_df['Delta'] - (self.option_df['CDF']))
            self.option_df['Delta Difference'] = delta_difference
            delta_ratio = abs(self.option_df['Delta'] / (self.option_df['CDF']))
            self.option_df['Delta Ratio'] = delta_ratio
            return self.option_df


def MC_call_option_price(strike_price, final_values, r, T):
    call_option_payoffs = np.maximum(0, final_values - strike_price)
    #positive_call_option_payoffs = call_option_payoffs[call_option_payoffs > 0]    #Use negative payoffs
    expected_payoff = np.mean(call_option_payoffs)
    call_option_price = np.exp(-r * T) * expected_payoff

    return call_option_price

def MC_put_option_price(strike_price, final_values, r, T):
    put_option_payoffs = np.maximum(0, strike_price - final_values)
    positive_put_option_payoffs = put_option_payoffs[put_option_payoffs > 0]
    
    if len(positive_put_option_payoffs) > 0:
        expected_payoff = np.mean(put_option_payoffs)
    else:
        expected_payoff = 0
    
    put_option_price = np.exp(-r * T) * expected_payoff    
    return put_option_price


def put_call_parity(S0: float, r: float, T: float, call_df, put_df): 
    strike_loop = call_df['Strike'].values
    parity_df = pd.DataFrame(columns=['Strike', 'LHS', 'RHS', 'Parity', 'Put Call Ratio', 'Total Volume'])   
    for strike in strike_loop:
        ultimo_value = call_df.loc[call_df['Strike'] == strike, 'Último'].values
        call_volume_value = call_df.loc[call_df['Strike'] == strike, 'Volume'].values
        delta = call_df.loc[call_df['Strike'] == strike, 'Delta'].values
        put_volume_value = put_df.loc[put_df['Strike'] == strike, 'Volume'].values

        # Left Hand Side
        if len(ultimo_value) > 0:
            ultimo_value = ultimo_value[0]
        else:
            ultimo_value = None
        lhs = ultimo_value + strike * np.exp(-r * T)

        # Put call Ratio
        if len(call_volume_value) > 0 and len(put_volume_value) > 0:
            pc_ratio = put_volume_value[0] / call_volume_value[0]
            total_volume = call_volume_value[0] + put_volume_value[0]
        else:
            pc_ratio = None

        # Right Hand Side
        put_ultimo_value = put_df.loc[put_df['Strike'] == strike, 'Último'].values
        if len(put_ultimo_value) > 0:
            put_ultimo_value = put_ultimo_value[0]
        else:
            put_ultimo_value = None
        rhs = put_ultimo_value + S0
        parity = lhs - rhs    
        row = pd.DataFrame({'Strike': [strike],'Call Delta': [delta],'Put Volume': [put_volume_value],'Call Volume': [call_volume_value], 'LHS': [lhs], 'RHS': [rhs], 'Parity': [parity], 'Put Call Ratio': [pc_ratio], 'Total Volume': [total_volume]})
        parity_df = pd.concat([parity_df, row], ignore_index=True)        
    
    # Min-Max Normalization
    scaler = MinMaxScaler()
    volume_data = parity_df['Total Volume'].values.reshape(-1, 1)
    volume_data_normalized = scaler.fit_transform(volume_data)
    parity_df['Normalized Total Volume'] = volume_data_normalized.flatten()
    parity_df['Put Volume'] = parity_df['Put Volume'].apply(lambda x: x[0])
    parity_df['Call Volume'] = parity_df['Call Volume'].apply(lambda x: x[0])
    return parity_df