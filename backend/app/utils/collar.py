import sys
import os
import json
import time
import cmath
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import OPLAB client
# Add parent directory to path to allow importing oplab
_backend_dir = Path(__file__).resolve().parent.parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))
from oplab import create_client

# Initialize OPLAB client (will use OPLAB_ACCESS_TOKEN from environment)
_oplab_client = create_client()

# Define the underlying assets
underlying = ["PETR4","VALE3", "BOVA11", "BBAS3", "BBDC4", "COGN3", "MGLU3", "ITUB4", "WEGE3", "EMBR3"]

call_bid = 'bid'  # change to bid/close if needed
put_ask = 'ask'  # change to ask/close if needed

def fetch_interest_rate(rate_id: str) -> Optional[Dict]:
    """
    Fetch interest rate data from the API.
    Args:
        rate_id (str): Interest rate ID ('CETIP' or 'SELIC')
    Returns:
        dict: Interest rate data or None if request fails
    """
    try:
        return _oplab_client.market.interest_rates.get_rate(rate_id)
    except Exception as e:
        print(f"Error fetching {rate_id} data: {str(e)}")
        return None

def fetch_underlying_data(underlying_symbols, max_retries=3, delay=5):
    all_data = []
    
    for symbol in underlying_symbols:
        for attempt in range(max_retries):
            try:
                data = _oplab_client.market.stocks.get_stock(symbol)
                
                if data is None:
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed for {symbol}: No data available")
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"Failed to retrieve data for {symbol} after {max_retries} attempts. Skipping...")
                        break
                
                # Filter the data to include only the desired fields
                filtered_data = {
                    "symbol": data.get("symbol"),
                    "type": data.get("type"),
                    "name": data.get("name"),
                    "open": data.get("open"),
                    "high": data.get("high"),
                    "low": data.get("low"),
                    "close": data.get("close"),
                    "volume": data.get("volume"),
                    "financial_volume": data.get("financial_volume"),
                    "trades": data.get("trades"),
                    "bid": data.get("bid"),
                    "ask": data.get("ask"),
                    "category": data.get("category"),
                    "contract_size": data.get("contract_size"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "parent_symbol": symbol  # Add parent_symbol to the filtered data
                }
                
                all_data.append(filtered_data)  # Append filtered data for each symbol
                break  # Exit retry loop if successful
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed to retrieve data for {symbol} after {max_retries} attempts. Skipping...")
    
    return all_data

def fetch_option_data(underlying_symbols, max_retries=3, delay=5):
    all_data = []
    
    for symbol in underlying_symbols:
        for attempt in range(max_retries):
            try:
                data = _oplab_client.market.options.list_options(symbol)
                
                if data is None:
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed for {symbol}: No data available")
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"Failed to retrieve data for {symbol} after {max_retries} attempts. Skipping...")
                        break
                
                # Add parent_symbol to each option in the data
                for option in data:
                    option['parent_symbol'] = symbol
                all_data.extend(data)  # Combine data from all symbols
                break  # Exit retry loop if successful
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed to retrieve data for {symbol} after {max_retries} attempts. Skipping...")
    
    return all_data

def save_raw_data_to_json(data, file_path):
    if not data:
        print("No data to save.")
        return
    
    # Save raw data to JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"Raw data saved to {file_path}")

def calculate_option_metrics(option, underlying_data):
    # Fetch the close price (spot_price) for the underlying asset
    parent_symbol = option.get('parent_symbol')
    spot_price = None

    # Find the underlying asset data for the parent_symbol
    for underlying_asset in underlying_data:
        if underlying_asset['symbol'] == parent_symbol:
            spot_price = underlying_asset.get('ask')
            break

    # If spot_price is not found, default to 0
    if spot_price is None:
        print(f"Warning: Could not find spot price for {parent_symbol}. Defaulting to 0.")
        spot_price = 0

    # Use the spot_price for calculations
    close_price = option.get(call_bid, 0)  # Change to bid if needed
    strike = option.get('strike', 0)
    days_to_maturity = option.get('days_to_maturity', 0)

    # Determine moneyness
    if strike > spot_price:
        moneyness = 'OTM'
    else:
        moneyness = 'ITM'

    # Calculate intrinsic and extrinsic values
    intrinsic_value = max(spot_price - strike, 0)
    extrinsic_value = max(close_price - intrinsic_value, 0)
    protection = intrinsic_value / spot_price if spot_price != 0 else 0
    pm = spot_price - close_price
    embedded_interest = extrinsic_value / spot_price if spot_price != 0 else 0
    annual_return = (1 + embedded_interest)**(252 / days_to_maturity) - 1 if days_to_maturity != 0 else 0

  

    # Add calculated metrics to the option
    option['moneyness'] = moneyness
    option['intrinsic_value'] = intrinsic_value
    option['extrinsic_value'] = extrinsic_value
    option['pm'] = pm
    option['protection'] = protection
    option['embedded_interest'] = embedded_interest
    option['annual_return'] = annual_return
    option['spot_price'] = spot_price  # Add spot_price to the option for reference

    return option

def save_processed_data_to_json(data, file_path):
    if not data:
        print("No data to save.")
        return
    
    # Save processed data to JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"Processed data saved to {file_path}")

def filter_and_attach_puts(data):
    for call_option in data:
        if call_option['category'] == 'CALL' and 'days_to_maturity' in call_option:
            # Filter out calls with zero or very low premiums (less than 0.01)
            if call_option.get('close', 0) < 0.01:
                continue
                
            pm = call_option.get('pm', 0)  # Ensure pm is correctly accessed
            put_options = [
                put for put in data
                if put['category'] == 'PUT'
                and 'days_to_maturity' in put
                and put['days_to_maturity'] == call_option['days_to_maturity']
                and 'strike' in put
                and put['parent_symbol'] == call_option['parent_symbol']
            ]
            
            # Sort put options by strike
            put_options_sorted = sorted(put_options, key=lambda x: x['strike'])
            
            # Find the index of the first put option with strike >= pm
            split_index = next((i for i, put in enumerate(put_options_sorted) if put['strike'] >= pm), len(put_options_sorted))
            
            # Select 4 puts below and 4 puts above (or as many as available if less than 4)
            puts_below = put_options_sorted[max(0, split_index-4):split_index]
            puts_above = put_options_sorted[split_index:split_index+4]
            
            selected_puts = puts_below + puts_above
            call_option['puts'] = []
            # Calculate PUT-specific metrics and remove CALL-specific metrics
            for put in selected_puts:
                # Use the correct field for put_ask (close in this case)
                put_price = put.get(put_ask, 0)  # This will use the 'close' price of the PUT

                # Filter out puts with zero or very low premiums (less than 0.01)
                if put_price < 0.01:
                    continue  # Skip to the next PUT strike in the loop
                
                # Calculate PUT-specific metrics
                extrinsic_value_result = call_option['extrinsic_value'] - put_price
                spot_price = call_option.get('spot_price', 0)
                embedded_interest_result = extrinsic_value_result / spot_price if spot_price != 0 else 0
                days_to_maturity = call_option.get('days_to_maturity', 0)
                pm_result = pm + put_price  # Corrected calculation of pm_result
                total_risk = put.get('strike', 0) - pm_result
                total_gain = call_option['strike'] - pm_result
                spot_variation_to_max_return = (call_option['strike'] - spot_price) / spot_price
                spot_variation_to_stoploss = (put.get('strike', 0) - spot_price) / spot_price
                spot_variation_to_pm_result = (pm_result - spot_price) / spot_price
                pm_distance_to_profit = (call_option['strike'] - pm_result) / pm_result
                pm_distance_to_loss = (put.get('strike', 0) - pm_result) / pm_result
                if call_option['protection'] > 0:
                    intrinsic_protection = True
                else:
                    intrinsic_protection = False
                if pm_distance_to_loss > -0.001:
                    zero_risk = True
                else:
                    zero_risk = False
                    
                # Calculate gain_to_risk_ratio
                if total_risk > -0.01 and total_gain > 0:                    
                    gain_to_risk_ratio = None
                elif total_risk <= -0.01:
                    gain_to_risk_ratio = total_gain / total_risk * (-1) if total_risk != 0 else 0
                
                # Skip this PUT if gain_to_risk_ratio is below 1 or None
                if gain_to_risk_ratio is None or gain_to_risk_ratio < 1:
                    continue
                
                # Handle potential complex number results
                try:
                    annual_return_result = (1 + embedded_interest_result)**(252 / days_to_maturity) - 1 if days_to_maturity != 0 else 0
                    if isinstance(annual_return_result, complex):
                        annual_return_result = annual_return_result.real
                except ValueError:
                    annual_return_result = 0

                try:
                    otm_annual_return_result = (1 + pm_distance_to_profit)**(252 / days_to_maturity) - 1 if days_to_maturity != 0 else 0
                    if isinstance(otm_annual_return_result, complex):
                        otm_annual_return_result = otm_annual_return_result.real
                except ValueError:
                    otm_annual_return_result = 0
                
                # Remove CALL-specific metrics from PUT
                for key in ['intrinsic_value', 'extrinsic_value', 'pm', 'protection', 'embedded_interest', 'annual_return', 'score']:
                    put.pop(key, None)
                
                # Add PUT-specific metrics
                put['extrinsic_value_result'] = extrinsic_value_result
                put['embedded_interest_result'] = embedded_interest_result
                put['pm_result'] = pm_result

                # Calculate combined score
                # Normalize spot_variation_to_max_return (lower is better)
                normalized_spot_variation_pm_result = 1 / (1 + abs(spot_variation_to_pm_result))  # Lower values are better
                # Normalize spot_variation_to_max_return (lower is better)
                normalized_spot_variation = 1 / (1 + abs(spot_variation_to_max_return))  # Lower values are better
                # Normalize pm_distance_to_loss (higher is better)
                normalized_pm_distance = pm_distance_to_loss  # Higher values are better
                # Normalize gain_to_risk_ratio (higher is better) - now with more importance
                normalized_gain_to_risk = gain_to_risk_ratio  # Higher values are better
                # Normalize annual_return_result (higher is better)
                normalized_annual_return = max(0, annual_return_result)  # Higher values are better

                # Assign weights (adjust as needed)
                weight_spot_variation_pm_result = 0.10  # Reduced weight
                weight_spot_variation = 0.05  # Reduced weight
                weight_pm_distance = 0.05  # Same weight
                weight_gain_to_risk = 0.10  # Adjusted weight for gain_to_risk_ratio
                weight_annual_return = 0.80  # Added weight for annual return

                # Calculate combined score
                combined_score = (
                    weight_spot_variation_pm_result * normalized_spot_variation_pm_result +
                    weight_spot_variation * normalized_spot_variation +
                    weight_pm_distance * normalized_pm_distance +
                    weight_gain_to_risk * normalized_gain_to_risk +
                    weight_annual_return * normalized_annual_return
                )

                # Add combined score to the PUT
                put['combined_score'] = combined_score

                call_option['puts'].append({
                    "symbol": put.get('symbol', ''),
                    "category": put.get('category', ''),
                    "days_to_maturity": put.get('days_to_maturity', 0),
                    "market_maker": put.get('market_maker', False),
                    "maturity_type": put.get('maturity_type', ''),
                    "strike": put.get('strike', ''),
                    "open": put.get('open', 0),
                    "high": put.get('high', 0),
                    "low": put.get('low', 0),
                    "close": put.get('close', 0),
                    "ask": put.get('ask', 0),
                    "bid": put.get('bid', 0),
                    "bid_volume": put.get('bid_volume', 0),
                    "ask_volume": put.get('ask_volume', 0),
                    "financial_volume": put.get('financial_volume', 0),
                    "extrinsic_value_result": extrinsic_value_result,
                    "embedded_interest_result": embedded_interest_result,
                    "annual_return_result": annual_return_result,
                    "pm_result": pm_result,
                    "total_risk": total_risk,
                    "total_gain": total_gain,
                    "gain_to_risk_ratio": gain_to_risk_ratio,
                    "spot_variation_to_max_return": spot_variation_to_max_return,
                    "spot_variation_to_stoploss": spot_variation_to_stoploss,
                    "spot_variation_to_pm_result": spot_variation_to_pm_result,        
                    "pm_distance_to_profit": pm_distance_to_profit, 
                    "pm_distance_to_loss": pm_distance_to_loss, 
                    "otm_annual_return_result": otm_annual_return_result,              
                    "zero_risk": zero_risk,
                    "intrinsic_protection": intrinsic_protection,
                    "combined_score": combined_score  # Add combined score
                })

            # Sort the puts by combined_score in descending order
            call_option['puts'] = sorted(call_option['puts'], key=lambda x: x.get('combined_score', 0), reverse=True)

    return data

import os
import json

def save_to_json(data, current_directory):
    # Get SELIC rate first
    selic_data = fetch_interest_rate('SELIC')
    if not selic_data or 'value' not in selic_data:
        print("Warning: Could not fetch SELIC rate. Using default value of 14.15")
        selic_rate = 14.15
    else:
        selic_rate = selic_data['value']

    # Filter data to include only CALL options with associated PUTs
    filtered_data = []
    for option in data:
        if option['category'] == 'CALL' and len(option.get('puts', [])) > 0:
            # Filter puts based on CDI relative return
            valid_puts = []
            for put in option['puts']:
                annual_return = put.get('annual_return_result', 0)
                cdi_relative_return = (annual_return * 100) / selic_rate
                
                if cdi_relative_return > 1:
                    put['cdi_relative_return'] = cdi_relative_return
                    valid_puts.append(put)
            
            if valid_puts and option.get('financial_volume', 0) > 1000:
                option['puts'] = valid_puts  # Replace puts with only valid ones
                filtered_data.append(option)

    # Helper function to get the maximum gain_to_risk_ratio from puts
    def max_gain_to_risk_ratio(option):
        puts = option.get('puts', [])
        ratios = [put.get('gain_to_risk_ratio', 0) for put in puts 
                  if put.get('gain_to_risk_ratio') is not None and put.get('gain_to_risk_ratio') > 0]
        return max(ratios) if ratios else 0

    # Sort data based on the highest gain_to_risk_ratio of associated puts
    sorted_data = sorted(filtered_data, key=max_gain_to_risk_ratio, reverse=True)
    
    # Remove unnecessary fields from all options
    sorted_data = filter_option_fields(sorted_data)

    # Split data into intrinsic and OTM categories
    intrinsic_data = [option for option in sorted_data if option.get('intrinsic_value', 0) > 0]
    otm_data = [option for option in sorted_data if option.get('intrinsic_value', 0) == 0]
    
    # Categorize intrinsic data based on days_to_maturity
    intrinsic_less_than_14 = [option for option in intrinsic_data if option.get('days_to_maturity', 0) < 14]
    intrinsic_between_15_and_30 = [option for option in intrinsic_data if 15 <= option.get('days_to_maturity', 0) < 30]
    intrinsic_between_30_and_60 = [option for option in intrinsic_data if 30 <= option.get('days_to_maturity', 0) < 60]
    intrinsic_more_than_60 = [option for option in intrinsic_data if option.get('days_to_maturity', 0) >= 60]
    
    # Categorize OTM data based on days_to_maturity
    otm_less_than_14 = [option for option in otm_data if option.get('days_to_maturity', 0) < 14]
    otm_between_15_and_30 = [option for option in otm_data if 15 <= option.get('days_to_maturity', 0) < 30]
    otm_between_30_and_60 = [option for option in otm_data if 30 <= option.get('days_to_maturity', 0) < 60]
    otm_more_than_60 = [option for option in otm_data if option.get('days_to_maturity', 0) >= 60]
    
    # Create organized structure
    organized_data = {
        "intrinsic": {
            "less_than_14_days": intrinsic_less_than_14,
            "between_15_and_30_days": intrinsic_between_15_and_30,
            "between_30_and_60_days": intrinsic_between_30_and_60,
            "more_than_60_days": intrinsic_more_than_60
        },
        "otm": {
            "less_than_14_days": otm_less_than_14,
            "between_15_and_30_days": otm_between_15_and_30,
            "between_30_and_60_days": otm_between_30_and_60,
            "more_than_60_days": otm_more_than_60
        }
    }
    
    # Ensure export directory exists - use utils/export
    export_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export")
    os.makedirs(export_directory, exist_ok=True)
    
    # Define file path for the single organized JSON file
    organized_json_path = os.path.join(export_directory, "collar_organized.json")
    
    # Save the organized data to file
    with open(organized_json_path, 'w', encoding='utf-8') as f:
        json.dump(organized_data, f, indent=4, ensure_ascii=False)
    print(f"Organized data saved to {organized_json_path}")

def get_collar_analysis() -> Dict[str, List[Dict[str, Any]]]:
    # Use the export directory in the utils folder
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export")
    
    collar_data = {
        "intrinsic": {},
        "otm": {}
    }
    
    categories = ["intrinsic", "otm"]
    maturity_ranges = [
        "less_than_14_days",
        "between_15_and_30_days",
        "between_30_and_60_days",
        "more_than_60_days"
    ]
    
    for category in categories:
        for maturity_range in maturity_ranges:
            file_name = f"{category}_options_{maturity_range}.json"
            file_path = os.path.join(export_dir, file_name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    collar_data[category][maturity_range] = data
            except FileNotFoundError:
                print(f"Warning: File not found at {file_path}")
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in file {file_path}")
    
    return collar_data

def filter_option_fields(options):
    """Filter out unnecessary fields from options data."""
    fields_to_remove = [
        'contract_size',
        'exchange_id',
        'isin',
        'security_category',
        'quotationForm'
    ]
    
    if isinstance(options, list):
        filtered_options = []
        for option in options:
            filtered_option = {key: value for key, value in option.items() if key not in fields_to_remove}
            
            # Also filter fields in 'puts' if they exist
            if 'puts' in filtered_option and isinstance(filtered_option['puts'], list):
                filtered_option['puts'] = [
                    {k: v for k, v in put.items() if k not in fields_to_remove}
                    for put in filtered_option['puts']
                ]
            
            filtered_options.append(filtered_option)
        return filtered_options
    else:
        # Handle single option case
        return {key: value for key, value in options.items() if key not in fields_to_remove}

def main():
    # Fetch underlying data
    underlying_data = fetch_underlying_data(underlying)
    
    # Fetch raw option data
    raw_data = fetch_option_data(underlying)
    
    # Calculate option metrics for each option using the underlying data
    processed_data = [calculate_option_metrics(option, underlying_data) for option in raw_data]
    
    # Filter and attach puts to calls
    processed_data_with_puts = filter_and_attach_puts(processed_data)
    
    # Save processed data to JSON files based on days_to_maturity
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Define the export directory
    export_directory = os.path.join(current_directory, "export")
    save_to_json(processed_data_with_puts, export_directory)

if __name__ == "__main__":
    main()