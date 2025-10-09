from flask_restful import Resource, reqparse
# from flask_cors import cross_origin  # Removed - using custom CORS middleware
import json
import os
import math
from datetime import datetime, timedelta
import traceback
import pandas as pd
import numpy as np  
from flask import jsonify, current_app, request, make_response
from ..utils import *
from ..utils.all_BR_recommendations import analyze_ibovlist, analyze_buy, analyze_strongbuy
from ..utils.cointegration_stocks import get_cointegration_data, get_pair_trading_signals, get_pair_details, get_recent_trading_signals
from ..utils.collar import get_collar_analysis
from ..utils.ddm_fluxo import get_fluxo_ddm_data
from ..utils.archive.dividend_calendar_utils import (
    get_dividend_calendar_data, 
    process_dividend_data, 
    get_dividend_summary,
    get_dividend_by_stock,
    get_upcoming_dividends
)


class RRGDataResource(Resource):
    def get(self):
        try:
            # Get the full path to the rrg_data.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, "utils", "export", "rrg_data.json")
            
            current_app.logger.info(f"Attempting to read RRG data from: {json_file_path}")
            
            # Read the JSON file
            with open(json_file_path, 'r') as file:
                rrg_data = json.load(file)
            
            current_app.logger.info(f"RRG data successfully retrieved")
            
            # Get query parameters
            symbol = request.args.get('symbol')
            min_rs_ratio = request.args.get('min_rs_ratio', type=float)
            max_rs_ratio = request.args.get('max_rs_ratio', type=float)
            min_rs_momentum = request.args.get('min_rs_momentum', type=float)
            max_rs_momentum = request.args.get('max_rs_momentum', type=float)
            quadrant = request.args.get('quadrant')  # leading, weakening, lagging, improving
            sort_by = request.args.get('sort_by', 'symbol')  # symbol, rs_ratio, rs_momentum
            sort_order = request.args.get('sort_order', 'asc')  # asc, desc
            limit = request.args.get('limit', type=int)
            date = request.args.get('date')  # Get data for specific date
            
            # Filter by symbol if provided
            filtered_data = {}
            if symbol:
                symbols = symbol.split(',')
                for sym in symbols:
                    if sym in rrg_data:
                        filtered_data[sym] = rrg_data[sym]
            else:
                filtered_data = rrg_data
            
            # Filter by quadrant if provided
            if quadrant:
                quadrant_map = {
                    'leading': {'min_rs_ratio': 100, 'min_rs_momentum': 100},
                    'weakening': {'min_rs_ratio': 100, 'max_rs_momentum': 100},
                    'lagging': {'max_rs_ratio': 100, 'max_rs_momentum': 100},
                    'improving': {'max_rs_ratio': 100, 'min_rs_momentum': 100}
                }
                
                if quadrant in quadrant_map:
                    q_filters = quadrant_map[quadrant]
                    if 'min_rs_ratio' in q_filters and min_rs_ratio is None:
                        min_rs_ratio = q_filters['min_rs_ratio']
                    if 'max_rs_ratio' in q_filters and max_rs_ratio is None:
                        max_rs_ratio = q_filters['max_rs_ratio']
                    if 'min_rs_momentum' in q_filters and min_rs_momentum is None:
                        min_rs_momentum = q_filters['min_rs_momentum']
                    if 'max_rs_momentum' in q_filters and max_rs_momentum is None:
                        max_rs_momentum = q_filters['max_rs_momentum']
            
            # Process and filter the data
            result = []
            for symbol_key, data in filtered_data.items():
                # Skip if the data doesn't have required fields
                if not all(k in data for k in ['Dates', 'RS_Ratio', 'RS_Momentum']):
                    continue
                
                # Get the data for each date and apply filters
                for i, date_val in enumerate(data['Dates']):
                    # Skip if we don't have enough data points
                    if i >= len(data['RS_Ratio']) or i >= len(data['RS_Momentum']):
                        continue
                    
                    # Skip if we're looking for a specific date and this isn't it
                    if date and date_val != date:
                        continue
                    
                    rs_ratio = data['RS_Ratio'][i]
                    rs_momentum = data['RS_Momentum'][i]
                    
                    # Apply numerical filters
                    if min_rs_ratio is not None and rs_ratio < min_rs_ratio:
                        continue
                    if max_rs_ratio is not None and rs_ratio > max_rs_ratio:
                        continue
                    if min_rs_momentum is not None and rs_momentum < min_rs_momentum:
                        continue
                    if max_rs_momentum is not None and rs_momentum > max_rs_momentum:
                        continue
                    
                    # If we reach here, all filters passed
                    result.append({
                        'symbol': symbol_key,
                        'date': date_val,
                        'rs_ratio': rs_ratio,
                        'rs_momentum': rs_momentum,
                        # Determine the quadrant based on values
                        'quadrant': 'leading' if rs_ratio >= 100 and rs_momentum >= 100 else
                                   'weakening' if rs_ratio >= 100 and rs_momentum < 100 else
                                   'lagging' if rs_ratio < 100 and rs_momentum < 100 else
                                   'improving'
                    })
            
            # Sort results if requested
            if sort_by == 'rs_ratio':
                result.sort(key=lambda x: x['rs_ratio'], reverse=(sort_order == 'desc'))
            elif sort_by == 'rs_momentum':
                result.sort(key=lambda x: x['rs_momentum'], reverse=(sort_order == 'desc'))
            else:  # Default sort by symbol
                result.sort(key=lambda x: x['symbol'], reverse=(sort_order == 'desc'))
            
            # Apply limit if provided
            if limit and len(result) > limit:
                result = result[:limit]
            
            # Get all unique symbols in the filtered result
            symbols_in_result = list(set([item['symbol'] for item in result]))
            
            # Count items in each quadrant
            quadrant_counts = {
                'leading': sum(1 for item in result if item['quadrant'] == 'leading'),
                'weakening': sum(1 for item in result if item['quadrant'] == 'weakening'),
                'lagging': sum(1 for item in result if item['quadrant'] == 'lagging'),
                'improving': sum(1 for item in result if item['quadrant'] == 'improving')
            }
            
            # Create the response
            response = {
                'metadata': {
                    'total_count': len(result),
                    'symbol_count': len(symbols_in_result),
                    'unique_symbols': symbols_in_result,
                    'quadrant_counts': quadrant_counts,
                    'filters_applied': {
                        'symbol': symbol,
                        'min_rs_ratio': min_rs_ratio,
                        'max_rs_ratio': max_rs_ratio,
                        'min_rs_momentum': min_rs_momentum,
                        'max_rs_momentum': max_rs_momentum,
                        'quadrant': quadrant,
                        'date': date
                    }
                },
                'results': result
            }
            
            return make_response(jsonify(response), 200)
        except Exception as e:
            current_app.logger.error(f"Error in RRGDataResource: {str(e)}")
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)

class BrRecommendationsResource(Resource):
    def get(self):
        try:
            # Get the full path to the all_BR_recommendations.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, "utils", "export", "all_BR_recommendations.json")
            
            current_app.logger.info(f"Attempting to read BR recommendations data from: {json_file_path}")
            
            # Read the JSON file
            with open(json_file_path, 'r') as file:
                recommendations_data = json.load(file)
            
            current_app.logger.info(f"BR recommendations data successfully retrieved")
            
            # Get query parameters
            symbol = request.args.get('symbol')
            analysis_type = request.args.get('analysis', 'raw')  # Default to raw data if no analysis type is provided
            
            # Filter by symbol if provided
            if symbol and symbol in recommendations_data:
                recommendations_data = {symbol: recommendations_data[symbol]}
                
            # Process response based on analysis_type
            result = None
            
            if analysis_type == 'ibov':
                from app.utils.all_BR_recommendations import analyze_ibovlist
                result = analyze_ibovlist(recommendations_data)
                
                # Filter out entries with NaN values
                if result:
                    # Filter out items with None or NaN values in key fields
                    filtered_result = []
                    for item in result:
                        has_nan = False
                        for key, value in item.items():
                            if value is None or (isinstance(value, float) and math.isnan(value)):
                                has_nan = True
                                break
                        if not has_nan:
                            filtered_result.append(item)
                    
                    result = filtered_result
                
                return make_response(jsonify({
                    "analysis": "IBOV stocks analysis",
                    "count": len(result),
                    "description": "Ibovespa stocks ranked by relevance with analyst data",
                    "results": result
                }), 200)
            
            elif analysis_type == 'b3':
                # Extract only the fields we need for B3 display
                formatted_data = {}
                for ticker, data in recommendations_data.items():
                    if isinstance(data, dict):  # Make sure the data is a dictionary
                        formatted_data[ticker] = {
                            "currentPrice": data.get("currentPrice"),
                            "targetHighPrice": data.get("targetHighPrice"),
                            "targetLowPrice": data.get("targetLowPrice"),
                            "targetMeanPrice": data.get("targetMeanPrice"),
                            "targetMedianPrice": data.get("targetMedianPrice"),
                            "recommendationMean": data.get("recommendationMean"),
                            "recommendationKey": data.get("recommendationKey", "none"),
                            "numberOfAnalystOpinions": data.get("numberOfAnalystOpinions"),
                            "averageAnalystRating": data.get("averageAnalystRating")
                        }                
                return make_response(jsonify({
                    "analysis": "B3 recommendations",
                    "count": len(formatted_data),
                    "description": "B3 stocks with analyst recommendations",
                    "results": formatted_data
                }), 200)
            
            elif analysis_type == 'buy':
                result = analyze_buy(recommendations_data)
                return make_response(jsonify({
                    "analysis": "Buy recommendations",
                    "description": "Stocks with analyst buy recommendations sorted by relevance",
                    "count": len(result),
                    "results": result
                }), 200)
            
            elif analysis_type == 'strong_buy':
                result = analyze_strongbuy(recommendations_data)
                return make_response(jsonify({
                    "analysis": "Strong Buy recommendations",
                    "description": "Stocks with analyst strong buy recommendations sorted by relevance",
                    "count": len(result),
                    "results": result
                }), 200)
                
            elif analysis_type == 'all_buy':
                # Combine both strong_buy and buy analyses
                strong_buys = analyze_strongbuy(recommendations_data)
                buys = analyze_buy(recommendations_data)
                
                # Add a type field to distinguish between them
                for item in strong_buys:
                    item['recommendation_type'] = 'strong_buy'
                
                for item in buys:
                    item['recommendation_type'] = 'buy'
                
                # Combine and sort by relevance - ensure all needed fields are preserved
                combined = strong_buys + buys
                
                # Make sure return_target_consensus is properly handled for all items
                for item in combined:
                    if 'return_target_consensus' not in item:
                        # Calculate it if missing using the same formula from the analyzer functions
                        item['return_target_consensus'] = (
                            (item.get('% Distance to Median', 0) * 0.4) + 
                            (item.get('% Distance to High', 0) * 0.3) + 
                            (item.get('% Distance to Mean', 0) * 0.3)
                        )
                
                # Sort combined results by score
                combined.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
                
                # Recalculate relevance ranking for the combined list
                for i, item in enumerate(combined):
                    item['relevance'] = i + 1
                    
                return make_response(jsonify({
                    "analysis": "All Buy recommendations (strong buy + buy)",
                    "description": "Combined analysis of strong buy and buy recommendations",
                    "count": len(combined),
                    "strong_buy_count": len(strong_buys),
                    "buy_count": len(buys),
                    "results": combined
                }), 200)
            
            else:
                # Return raw data
                return make_response(jsonify({
                    "analysis": "Raw data",
                    "count": len(recommendations_data),
                    "results": recommendations_data
                }), 200)
                
        except Exception as e:
            current_app.logger.error(f"Error in BrRecommendationsResource: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)

class ScreenerRSIResource(Resource):
    def get(self):
        try:
            # Get the full path to the screener_overbought_oversold_rsi_results.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, "utils", "export", "screener_overbought_oversold_rsi_results.json")
            
            current_app.logger.info(f"Attempting to read RSI screener data from: {json_file_path}")
            
            # Read the JSON file
            with open(json_file_path, 'r') as file:
                rsi_data = json.load(file)
            
            current_app.logger.info(f"RSI screener data successfully retrieved")
            
            # Get query parameters
            timeframe = request.args.get('timeframe')  # e.g., 15m, 60m, 1d, 1wk
            condition = request.args.get('condition')  # overbought or oversold
            
            # Filter by timeframe if provided
            if timeframe:
                timeframe_key = f"stockdata_{timeframe}"
                if timeframe_key in rsi_data:
                    filtered_data = {timeframe_key: rsi_data[timeframe_key]}
                    
                    # Further filter by condition if provided
                    if condition and condition in rsi_data[timeframe_key]:
                        filtered_data[timeframe_key] = {
                            condition: rsi_data[timeframe_key][condition]
                        }
                    
                    return make_response(jsonify(filtered_data), 200)
                else:
                    return make_response(jsonify({'error': f'Timeframe {timeframe} not found'}), 404)
            
            # Return all data if no filters are applied
            return make_response(jsonify(rsi_data), 200)
            
        except Exception as e:
            current_app.logger.error(f"Error in ScreenerRSIResource: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)

class VolatilitySurfaceResource(Resource):
    # Cache for volatility data to avoid repeated file operations
    _cache = {
        'data': None,
        'last_updated': None,
        'aggregated_data': {}  # Cache for aggregated/downsampled data
    }
    
    def get(self):
        try:
            # Get query parameters
            symbol = request.args.get('symbol')
            option_type = request.args.get('option_type')  # CALL or PUT
            expiry_date = request.args.get('expiry_date')  # Filter by specific expiry date
            maturity_type = request.args.get('maturity_type')  # AMERICAN or EUROPEAN
            moneyness = request.args.get('moneyness')  # ITM, ATM, OTM
            
            # NEW: Resolution parameter for data sampling
            resolution = request.args.get('resolution', 'high')  # high, medium, low
            
            # NEW: Format parameter to return the data in the desired format
            data_format = request.args.get('format', 'surface')  # surface, grid, summary
            
            # Get the full path to the volatility_surface.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, "utils", "export", "volatility_surface.json")
            
            # Check if data is already cached and file hasn't been modified
            file_mtime = os.path.getmtime(json_file_path)
            
            if (self._cache['data'] is None or 
                self._cache['last_updated'] is None or 
                self._cache['last_updated'] < file_mtime):
                
                current_app.logger.info(f"Loading volatility surface data from file: {json_file_path}")
                
                # Read the JSON file
                with open(json_file_path, 'r') as file:
                    volatility_data = json.load(file)
                
                # Cache the data and update timestamp
                self._cache['data'] = volatility_data
                self._cache['last_updated'] = file_mtime
                self._cache['aggregated_data'] = {}  # Reset aggregated data cache
                
                current_app.logger.info(f"Volatility surface data cached successfully")
            else:
                volatility_data = self._cache['data']
                current_app.logger.info(f"Using cached volatility surface data")
            
            result = {}
            
            # If symbol is provided and exists in the data
            if symbol:
                if symbol in volatility_data:
                    result[symbol] = volatility_data[symbol]
                else:
                    return make_response(jsonify({'error': f'Symbol {symbol} not found'}), 404)
            else:
                # Return list of available symbols only instead of all data
                if data_format == 'list':
                    available_symbols = list(volatility_data.keys())
                    return make_response(jsonify({
                        'symbols': available_symbols,
                        'count': len(available_symbols)
                    }), 200)
                else:
                    result = volatility_data  # Return all data if no symbol specified
            
            # Process each symbol in the result
            for key in list(result.keys()):
                if isinstance(result[key], list):
                    # Create a cache key for this specific request
                    cache_key = f"{key}_{option_type}_{expiry_date}_{maturity_type}_{moneyness}_{resolution}_{data_format}"
                    
                    # Check if we have this result cached
                    if cache_key in self._cache['aggregated_data']:
                        result[key] = self._cache['aggregated_data'][cache_key]
                        current_app.logger.info(f"Using cached processed data for {cache_key}")
                        continue
                    
                    # Preprocess to add missing fields for incomplete entries
                    options_with_complete_data = []
                    for option in result[key]:
                        if not isinstance(option, dict):
                            continue
                        
                        # Keep only entries with bs value (essential for visualization)
                        if 'bs' not in option:
                            continue
                            
                        # NEW: Ensure the option has required fields for visualization
                        if 'strike' not in option:
                            # For simple data entries with just 'bs', skip or add defaults
                            # based on the visualization requirements
                            continue
                        
                        options_with_complete_data.append(option)
                    
                    # Apply filters
                    filtered_options = []
                    for option in options_with_complete_data:
                        include = True
                        
                        if option_type and 'type' in option and option['type'] != option_type:
                            include = False
                            
                        if expiry_date and 'due_date' in option:
                            option_date = option['due_date'].split('T')[0] if 'T' in option['due_date'] else option['due_date']
                            if option_date != expiry_date:
                                include = False
                                
                        if maturity_type and 'maturity_type' in option and option['maturity_type'] != maturity_type:
                            include = False
                            
                        if moneyness and 'moneyness' in option and option['moneyness'] != moneyness:
                            include = False
                            
                        if include:
                            filtered_options.append(option)
                    
                    # If no options left after filtering, continue with empty list
                    if not filtered_options:
                        result[key] = []
                        continue
                    
                    # Apply resolution-based sampling to reduce data size
                    sampled_options = filtered_options
                    if resolution == 'low':
                        # Keep ~20% of the data points
                        sample_size = max(10, len(filtered_options) // 5)
                        indices = np.linspace(0, len(filtered_options)-1, sample_size, dtype=int)
                        sampled_options = [filtered_options[i] for i in indices]
                    elif resolution == 'medium':
                        # Keep ~50% of the data points
                        sample_size = max(20, len(filtered_options) // 2)
                        indices = np.linspace(0, len(filtered_options)-1, sample_size, dtype=int)
                        sampled_options = [filtered_options[i] for i in indices]
                    
                    # Format the output based on the requested format
                    if data_format == 'surface':
                        # For 3D surface visualization - return full option objects
                        processed_data = sampled_options
                    elif data_format == 'grid':
                        # For grid visualization - group by strike and expiry to create a grid
                        strike_expiry_map = {}
                        for option in sampled_options:
                            strike = option.get('strike')
                            expiry = option.get('due_date')
                            
                            if strike is not None and expiry is not None:
                                if strike not in strike_expiry_map:
                                    strike_expiry_map[strike] = {}
                                
                                if expiry not in strike_expiry_map[strike]:
                                    strike_expiry_map[strike][expiry] = option.get('bs')
                        
                        processed_data = {
                            'strikes': sorted(list(strike_expiry_map.keys())),
                            'expiries': sorted(list(set([e for s in strike_expiry_map.values() for e in s.keys()]))),
                            'values': strike_expiry_map
                        }
                    elif data_format == 'summary':
                        # For summary view - provide statistics about the data
                        bs_values = [o.get('bs') for o in sampled_options if o.get('bs') is not None]
                        
                        if bs_values:
                            processed_data = {
                                'count': len(sampled_options),
                                'min_bs': min(bs_values),
                                'max_bs': max(bs_values),
                                'avg_bs': sum(bs_values) / len(bs_values),
                                'option_types': list(set([o.get('type') for o in sampled_options if 'type' in o])),
                                'expiry_dates': list(set([o.get('due_date') for o in sampled_options if 'due_date' in o])),
                                'maturity_types': list(set([o.get('maturity_type') for o in sampled_options if 'maturity_type' in o]))
                            }
                        else:
                            processed_data = {
                                'count': 0,
                                'error': 'No valid data points found'
                            }
                    else:
                        # Default: just return the sampled options
                        processed_data = sampled_options
                    
                    # Store in cache for future requests
                    self._cache['aggregated_data'][cache_key] = processed_data
                    result[key] = processed_data
            
            return make_response(jsonify(result), 200)
            
        except Exception as e:
            current_app.logger.error(f"Error in VolatilitySurfaceResource: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)

class CollarResource(Resource):
    # Cache for collar data to avoid repeated file operations
    _cache = {
        'data': None,
        'last_updated': None
    }
    
    def get(self):
        try:
            # Get query parameters
            category = request.args.get('category')  # intrinsic or otm
            maturity_range = request.args.get('maturity_range')  # less_than_14_days, between_15_and_30_days, etc.
            symbol = request.args.get('symbol')  # Filter by underlying symbol
            min_gain_to_risk = request.args.get('min_gain_to_risk', type=float)  # Minimum gain to risk ratio
            sort_by = request.args.get('sort_by', 'gain_to_risk_ratio')  # Field to sort by
            sort_order = request.args.get('sort_order', 'desc')  # asc or desc
            limit = request.args.get('limit', type=int)  # Limit number of results
            
            # Get the full path to the collar_organized.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, "utils", "export", "collar_organized.json")
            
            # Check if data is already cached and file hasn't been modified
            file_mtime = os.path.getmtime(json_file_path)
            
            if (self._cache['data'] is None or 
                self._cache['last_updated'] is None or 
                self._cache['last_updated'] < file_mtime):
                
                current_app.logger.info(f"Loading collar strategy data from file: {json_file_path}")
                
                # Read the JSON file
                with open(json_file_path, 'r') as file:
                    collar_data = json.load(file)
                
                # Cache the data and update timestamp
                self._cache['data'] = collar_data
                self._cache['last_updated'] = file_mtime
                
                current_app.logger.info(f"Collar strategy data cached successfully")
            else:
                collar_data = self._cache['data']
                current_app.logger.info(f"Using cached collar strategy data")
            
            # Filter by category if provided
            if category and category in collar_data:
                filtered_data = {category: collar_data[category]}
                
                # Further filter by maturity_range if provided
                if maturity_range and maturity_range in collar_data[category]:
                    filtered_data[category] = {
                        maturity_range: collar_data[category][maturity_range]
                    }
            else:
                filtered_data = collar_data
            
            # Apply additional filters and processing
            result = self._process_collar_data(filtered_data, symbol, min_gain_to_risk, sort_by, sort_order, limit)
            
            # Return the filtered and processed data
            return make_response(jsonify(result), 200)
            
        except Exception as e:
            current_app.logger.error(f"Error in CollarResource: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)
    
    def _process_collar_data(self, data, symbol=None, min_gain_to_risk=None, sort_by='gain_to_risk_ratio', sort_order='desc', limit=None):
        result = {}
        
        # Process the data structure
        for category, maturity_ranges in data.items():
            result[category] = {}
            
            for m_range, options in maturity_ranges.items():
                # Flatten all calls with their puts for easier filtering
                flattened_options = []
                
                for call in options:
                    # Skip if not a proper call option object
                    if not isinstance(call, dict):
                        continue
                        
                    # Filter by symbol if provided
                    if symbol and call.get('parent_symbol') != symbol:
                        continue
                    
                    # Extract the puts from each call
                    puts = call.get('puts', [])
                    
                    # Process each put attached to this call
                    for put in puts:
                        # Skip if not a proper put option object
                        if not isinstance(put, dict):
                            continue
                            
                        # Filter out puts with zero or very low premiums (less than 0.01)
                        put_premium = put.get('close', 0)
                        if put_premium < 0.01:
                            continue
                            
                        # Filter by minimum gain_to_risk_ratio if provided
                        if min_gain_to_risk is not None and (
                            'gain_to_risk_ratio' not in put or 
                            put['gain_to_risk_ratio'] is None or 
                            put['gain_to_risk_ratio'] < min_gain_to_risk
                        ):
                            continue
                        
                        # Create a combined entry with both call and put data
                        combined = {
                            'call': {k: v for k, v in call.items() if k != 'puts'},
                            'put': put,
                            'strategy': {
                                'parent_symbol': call.get('parent_symbol'),
                                'days_to_maturity': call.get('days_to_maturity'),
                                'maturity_type': put.get('maturity_type'),
                                'gain_to_risk_ratio': put.get('gain_to_risk_ratio'),
                                'combined_score': put.get('combined_score'),
                                'intrinsic_protection': put.get('intrinsic_protection', False),
                                'zero_risk': put.get('zero_risk', False),
                                'pm_result': put.get('pm_result'),
                                'cdi_relative_return': put.get('cdi_relative_return'),
                                'call_symbol': call.get('symbol'),
                                'put_symbol': put.get('symbol'),
                                'call_strike': call.get('strike'),
                                'put_strike': put.get('strike'),
                                'total_gain': put.get('total_gain'),
                                'total_risk': put.get('total_risk')
                            }
                        }
                        
                        flattened_options.append(combined)
                
                # Sort the flattened options
                if sort_by == 'gain_to_risk_ratio':
                    # Default sorting by gain_to_risk_ratio
                    flattened_options.sort(
                        key=lambda x: (
                            x['strategy'].get('gain_to_risk_ratio', 0) 
                            if x['strategy'].get('gain_to_risk_ratio') is not None 
                            else 0
                        ), 
                        reverse=(sort_order == 'desc')
                    )
                elif sort_by == 'combined_score':
                    # Sort by combined score
                    flattened_options.sort(
                        key=lambda x: (
                            x['strategy'].get('combined_score', 0) 
                            if x['strategy'].get('combined_score') is not None 
                            else 0
                        ), 
                        reverse=(sort_order == 'desc')
                    )
                elif sort_by == 'days_to_maturity':
                    # Sort by days to maturity
                    flattened_options.sort(
                        key=lambda x: x['strategy'].get('days_to_maturity', 0), 
                        reverse=(sort_order == 'desc')
                    )
                
                # Apply limit if provided
                if limit and len(flattened_options) > limit:
                    flattened_options = flattened_options[:limit]
                
                # Store the processed options in the result
                result[category][m_range] = flattened_options
        
        # Add metadata to the response
        metadata = self._generate_metadata(result)
        
        return {
            "metadata": metadata,
            "results": result
        }
    
    def _generate_metadata(self, data):
        total_count = 0
        symbols = set()
        category_counts = {}
        maturity_range_counts = {}
        
        # Calculate counts and extract symbols
        for category, maturity_ranges in data.items():
            category_counts[category] = 0
            
            for m_range, options in maturity_ranges.items():
                count = len(options)
                total_count += count
                category_counts[category] += count
                
                if m_range not in maturity_range_counts:
                    maturity_range_counts[m_range] = 0
                maturity_range_counts[m_range] += count
                
                # Extract unique symbols
                for option in options:
                    if 'strategy' in option and 'parent_symbol' in option['strategy']:
                        symbols.add(option['strategy']['parent_symbol'])
        
        return {
            "total_count": total_count,
            "symbol_count": len(symbols),
            "unique_symbols": list(symbols),
            "category_counts": category_counts,
            "maturity_range_counts": maturity_range_counts
        }

class CoveredCallResource(Resource):
    # Cache for covered call data to avoid repeated file operations
    _cache = {
        'data': None,
        'last_updated': None
    }
    
    def get(self):
        try:
            # Get query parameters
            maturity_range = request.args.get('maturity_range')  # less_than_14_days, between_15_and_30_days, etc.
            symbol = request.args.get('symbol')  # Filter by underlying symbol
            min_cdi_relative_return = request.args.get('min_cdi_relative_return', type=float)  # Minimum CDI relative return
            sort_by = request.args.get('sort_by', 'cdi_relative_return')  # Field to sort by
            sort_order = request.args.get('sort_order', 'desc')  # asc or desc
            limit = request.args.get('limit', type=int)  # Limit number of results
            
            # Get the full path to the covered_calls_organized.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, "utils", "export", "covered_calls_organized.json")
            
            # Check if data is already cached and file hasn't been modified
            file_mtime = os.path.getmtime(json_file_path)
            
            if (self._cache['data'] is None or 
                self._cache['last_updated'] is None or 
                self._cache['last_updated'] < file_mtime):
                
                current_app.logger.info(f"Loading covered call strategy data from file: {json_file_path}")
                
                # Read the JSON file
                with open(json_file_path, 'r') as file:
                    covered_call_data = json.load(file)
                
                # Cache the data and update timestamp
                self._cache['data'] = covered_call_data
                self._cache['last_updated'] = file_mtime
                
                current_app.logger.info(f"Covered call strategy data cached successfully")
            else:
                covered_call_data = self._cache['data']
                current_app.logger.info(f"Using cached covered call strategy data")
            
            result = {}
            unique_symbols = set()
            total_options = 0
            
            # Filter by maturity range if provided
            if maturity_range and maturity_range in covered_call_data:
                filtered_data = {maturity_range: covered_call_data[maturity_range]}
            else:
                filtered_data = covered_call_data
            
            # Process each maturity range in the filtered data
            for range_key, options in filtered_data.items():
                filtered_options = []
                
                # Apply filters to each option
                for option in options:
                    # Skip if not a proper option object
                    if not isinstance(option, dict):
                        continue
                    
                    # Filter out options with zero or very low premiums (less than 0.01)
                    bid_price = option.get('bid', 0)
                    if bid_price < 0.01:
                        continue
                    
                    # Filter by symbol if provided
                    if symbol and option.get('parent_symbol') != symbol:
                        continue
                    
                    # Filter by minimum cdi_relative_return if provided
                    if min_cdi_relative_return is not None:
                        if 'cdi_relative_return' not in option or option['cdi_relative_return'] < min_cdi_relative_return:
                            continue
                    
                    # If we reach here, all filters passed
                    filtered_options.append(option)
                    
                    # Collect unique symbols
                    if 'parent_symbol' in option:
                        unique_symbols.add(option['parent_symbol'])
                
                # Apply sorting if there are options in this range
                if filtered_options:
                    # Sort by the requested field
                    if sort_by in filtered_options[0]:
                        filtered_options.sort(
                            key=lambda x: x.get(sort_by, 0) if x.get(sort_by) is not None else 0,
                            reverse=(sort_order == 'desc')
                        )
                    
                    # Apply limit if provided
                    if limit and len(filtered_options) > limit:
                        filtered_options = filtered_options[:limit]
                    
                    total_options += len(filtered_options)
                
                # Store the processed options in the result
                result[range_key] = filtered_options
            
            # Create metadata for the response
            metadata = {
                "total_count": total_options,
                "symbol_count": len(unique_symbols),
                "unique_symbols": list(unique_symbols),
                "maturity_ranges": list(result.keys()),
                "filters_applied": {
                    "maturity_range": maturity_range,
                    "symbol": symbol,
                    "min_cdi_relative_return": min_cdi_relative_return,
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                    "limit": limit
                }
            }
            
            # Return the filtered and processed data
            return make_response(jsonify({
                "metadata": metadata,
                "results": result
            }), 200)
            
        except Exception as e:
            current_app.logger.error(f"Error in CoveredCallResource: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)

class PairsTradingResource(Resource):
    # Cache for pairs trading data to avoid repeated file operations
    _cache = {
        'cointegration_data': None,
        'trading_signals_data': None,
        'cointegration_last_updated': None,
        'trading_signals_last_updated': None
    }
    
    def get(self):
        try:
            # Get the full paths to the data files
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cointegration_path = os.path.join(base_dir, "utils", "export", "combined_cointegration_results.json")
            signals_path = os.path.join(base_dir, "utils", "export", "recent_trading_signals.json")
            
            # Update the cache if needed
            self._update_cache(cointegration_path, signals_path)
            
            # Get query parameters
            data_type = request.args.get('data_type', 'all')  # all, cointegration, signals
            period = request.args.get('period', 'last_6_months')
            asset1 = request.args.get('asset1')
            asset2 = request.args.get('asset2')
            signal_type = request.args.get('signal_type')  # buy, sell
            min_zscore = request.args.get('min_zscore', type=float)
            max_zscore = request.args.get('max_zscore', type=float)
            min_beta = request.args.get('min_beta', type=float)
            max_beta = request.args.get('max_beta', type=float)
            min_half_life = request.args.get('min_half_life', type=float)
            max_half_life = request.args.get('max_half_life', type=float)
            sort_by = request.args.get('sort_by', 'signal_date')
            sort_order = request.args.get('sort_order', 'desc')
            limit = request.args.get('limit', 50, type=int)
            
            # Filter by cointegrated only by default
            cointegrated_only = request.args.get('cointegrated_only', 'true').lower() == 'true'
            
            response = {
                "metadata": {
                    "filters_applied": {
                        "data_type": data_type,
                        "period": period,
                        "asset1": asset1,
                        "asset2": asset2,
                        "signal_type": signal_type,
                        "min_zscore": min_zscore,
                        "max_zscore": max_zscore,
                        "min_beta": min_beta,
                        "max_beta": max_beta,
                        "min_half_life": min_half_life,
                        "max_half_life": max_half_life,
                        "cointegrated_only": cointegrated_only
                    }
                }
            }
            
            # Handle specific asset pair details request
            if asset1 and asset2 and data_type == 'pair_details':
                pair_details = get_pair_details(asset1, asset2, period)
                return make_response(jsonify(pair_details), 200)
            
            # Get cointegration data if requested
            if data_type in ['all', 'cointegration']:
                cointegration_data = self._get_cointegration_data(period, asset1, asset2, cointegrated_only)
                response["cointegration"] = cointegration_data
            
            # Get trading signals if requested
            if data_type in ['all', 'signals']:
                signals_data = self._get_trading_signals(
                    asset1, asset2, signal_type, min_zscore, max_zscore, 
                    min_beta, max_beta, min_half_life, max_half_life,
                    sort_by, sort_order, limit
                )
                response["signals"] = signals_data
            
            return make_response(jsonify(response), 200)
            
        except Exception as e:
            current_app.logger.error(f"Error in PairsTradingResource: {str(e)}")
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)
    
    def _update_cache(self, cointegration_path, signals_path):
        """Update the cache if the files have been modified"""
        try:
            # Check cointegration file
            if os.path.exists(cointegration_path):
                last_modified = os.path.getmtime(cointegration_path)
                if self._cache['cointegration_last_updated'] != last_modified:
                    with open(cointegration_path, 'r') as file:
                        self._cache['cointegration_data'] = json.load(file)
                    self._cache['cointegration_last_updated'] = last_modified
            
            # Check signals file
            if os.path.exists(signals_path):
                last_modified = os.path.getmtime(signals_path)
                if self._cache['trading_signals_last_updated'] != last_modified:
                    with open(signals_path, 'r') as file:
                        self._cache['trading_signals_data'] = json.load(file)
                    self._cache['trading_signals_last_updated'] = last_modified
                    
        except Exception as e:
            current_app.logger.error(f"Error updating cache: {str(e)}")
            
    def _get_cointegration_data(self, period, asset1=None, asset2=None, cointegrated_only=True):
        """Filter and return cointegration data"""
        if not self._cache['cointegration_data'] or period not in self._cache['cointegration_data']:
            return {"results": [], "summary": {"total_pairs": 0}}
            
        # Get the data for the selected period
        period_data = self._cache['cointegration_data'].get(period, {})
        results = period_data.get("results", [])
        
        # Filter the results
        filtered_results = []
        for pair in results:
            # Skip if we need only cointegrated pairs and this is not cointegrated
            if cointegrated_only and not pair.get("cointegrated", False):
                continue
                
            # Filter by assets if specified
            if asset1 and asset2:
                if not ((pair.get("asset1") == asset1 and pair.get("asset2") == asset2) or 
                        (pair.get("asset1") == asset2 and pair.get("asset2") == asset1)):
                    continue
            elif asset1:
                if pair.get("asset1") != asset1 and pair.get("asset2") != asset1:
                    continue
            elif asset2:
                if pair.get("asset1") != asset2 and pair.get("asset2") != asset2:
                    continue
                
            filtered_results.append(pair)
            
        # Create a summary of filtered data
        cointegrated_count = sum(1 for pair in filtered_results if pair.get("cointegrated", False))
        total_count = len(filtered_results)
        
        return {
            "results": filtered_results,
            "summary": {
                "total_pairs": total_count,
                "cointegrated_pairs": cointegrated_count,
                "cointegrated_percentage": (cointegrated_count / total_count * 100) if total_count > 0 else 0
            }
        }
        
    def _get_trading_signals(self, asset1=None, asset2=None, signal_type=None, 
                             min_zscore=None, max_zscore=None,
                             min_beta=None, max_beta=None,
                             min_half_life=None, max_half_life=None,
                             sort_by='signal_date', sort_order='desc', limit=50):
        """Filter and return trading signals data"""
        if not self._cache['trading_signals_data']:
            return {"signals": [], "summary": {"total_signals": 0}}
            
        signals = self._cache['trading_signals_data'].get("last_5_days_signals", [])
        
        # Filter the signals
        filtered_signals = []
        for signal in signals:
            # Filter by assets if specified
            if asset1 and asset2:
                if not ((signal.get("asset1") == asset1 and signal.get("asset2") == asset2) or 
                        (signal.get("asset1") == asset2 and signal.get("asset2") == asset1)):
                    continue
            elif asset1:
                if signal.get("asset1") != asset1 and signal.get("asset2") != asset1:
                    continue
            elif asset2:
                if signal.get("asset1") != asset2 and signal.get("asset2") != asset2:
                    continue
                
            # Filter by signal type
            if signal_type and signal.get("signal_type") != signal_type:
                continue
                
            # Filter by z-score
            current_zscore = signal.get("current_zscore")
            if current_zscore is not None:
                if min_zscore is not None and current_zscore < min_zscore:
                    continue
                if max_zscore is not None and current_zscore > max_zscore:
                    continue
            
            # Filter by beta (hedge ratio)
            beta = signal.get("beta")
            if beta is not None:
                if min_beta is not None and beta < min_beta:
                    continue
                if max_beta is not None and beta > max_beta:
                    continue
            
            # Filter by half-life (mean reversion speed in days)
            half_life = signal.get("half_life")
            if half_life is not None:
                if min_half_life is not None and half_life < min_half_life:
                    continue
                if max_half_life is not None and half_life > max_half_life:
                    continue
            
            filtered_signals.append(signal)
            
        # Sort the signals
        if sort_by in ['signal_date', 'current_zscore', 'p_value', 'beta', 'half_life']:
            try:
                filtered_signals.sort(
                    key=lambda x: x.get(sort_by, 0) if x.get(sort_by) is not None else float('inf' if sort_order == 'asc' else '-inf'), 
                    reverse=(sort_order == 'desc')
                )
            except Exception as e:
                current_app.logger.error(f"Error sorting signals: {str(e)}")
                # Fall back to signal_date if there's an error
                filtered_signals.sort(
                    key=lambda x: x.get('signal_date', ''), 
                    reverse=True
                )
            
        # Apply limit
        if limit and len(filtered_signals) > limit:
            filtered_signals = filtered_signals[:limit]
            
        # Create a summary of filtered data
        buy_count = sum(1 for signal in filtered_signals if signal.get("signal_type") == "buy")
        sell_count = sum(1 for signal in filtered_signals if signal.get("signal_type") == "sell")
        
        # Add beta and half_life statistics to summary
        beta_values = [s.get("beta") for s in filtered_signals if s.get("beta") is not None]
        half_life_values = [s.get("half_life") for s in filtered_signals if s.get("half_life") is not None]
        
        beta_stats = {}
        if beta_values:
            beta_stats = {
                "min": min(beta_values),
                "max": max(beta_values),
                "avg": sum(beta_values) / len(beta_values)
            }
            
        half_life_stats = {}
        if half_life_values:
            half_life_stats = {
                "min": min(half_life_values),
                "max": max(half_life_values),
                "avg": sum(half_life_values) / len(half_life_values)
            }
        
        return {
            "signals": filtered_signals,
            "summary": {
                "total_signals": len(filtered_signals),
                "buy_signals": buy_count,
                "sell_signals": sell_count,
                "beta_stats": beta_stats,
                "half_life_stats": half_life_stats
            }
        }

class IBOVStocksResource(Resource):
    # Cache for IBOV stocks data to avoid repeated file operations
    _cache = {
        'data': None,
        'last_updated': None
    }

    def get(self):
        try:
            # Get query parameters
            symbol = request.args.get('symbol')
            min_iv_current = request.args.get('min_iv_current', type=float)
            max_iv_current = request.args.get('max_iv_current', type=float)
            min_beta_ibov = request.args.get('min_beta_ibov', type=float)
            max_beta_ibov = request.args.get('max_beta_ibov', type=float)
            min_iv_ewma_ratio = request.args.get('min_iv_ewma_ratio', type=float)
            max_iv_ewma_ratio = request.args.get('max_iv_ewma_ratio', type=float)
            sort_by = request.args.get('sort_by', 'symbol')  # Default sort by symbol
            sort_order = request.args.get('sort_order', 'asc')  # Default sort order
            limit = request.args.get('limit', type=int)
            
            # Get the full path to the IBOV_stocks.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, "utils", "export", "IBOV_stocks.json")
            
            # Check if data is already cached and file hasn't been modified
            file_mtime = os.path.getmtime(json_file_path)
            
            if (self._cache['data'] is None or 
                self._cache['last_updated'] is None or 
                self._cache['last_updated'] < file_mtime):
                
                current_app.logger.info(f"Loading IBOV stocks data from file: {json_file_path}")
                
                # Read the JSON file with explicit UTF-8 encoding
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    stocks_data = json.load(file)
                
                # Calculate iv_ewma_ratio for each stock if not already present
                for stock in stocks_data:
                    if isinstance(stock, dict) and 'iv_ewma_ratio' not in stock:
                        iv_current = stock.get('iv_current')
                        ewma_current = stock.get('ewma_current')
                        if iv_current is not None and ewma_current is not None and ewma_current != 0:
                            stock['iv_ewma_ratio'] = iv_current / ewma_current
                        else:
                            stock['iv_ewma_ratio'] = None
                
                # Cache the data and update timestamp
                self._cache['data'] = stocks_data
                self._cache['last_updated'] = file_mtime
                
                current_app.logger.info(f"IBOV stocks data cached successfully")
            else:
                stocks_data = self._cache['data']
                current_app.logger.info(f"Using cached IBOV stocks data")
            
            # Filter the data
            filtered_data = []
            for stock in stocks_data:
                # Skip if not a proper stock object
                if not isinstance(stock, dict):
                    continue
                
                # Filter by symbol if provided
                if symbol and stock.get('symbol') != symbol:
                    continue
                
                # Filter by iv_current range if provided
                iv_current = stock.get('iv_current')
                if iv_current is not None:
                    if min_iv_current is not None and iv_current < min_iv_current:
                        continue
                    if max_iv_current is not None and iv_current > max_iv_current:
                        continue
                
                # Filter by beta_ibov range if provided
                beta_ibov = stock.get('beta_ibov')
                if beta_ibov is not None:
                    if min_beta_ibov is not None and beta_ibov < min_beta_ibov:
                        continue
                    if max_beta_ibov is not None and beta_ibov > max_beta_ibov:
                        continue
                
                # Filter by iv_ewma_ratio range if provided
                iv_ewma_ratio = stock.get('iv_ewma_ratio')
                if iv_ewma_ratio is not None:
                    if min_iv_ewma_ratio is not None and iv_ewma_ratio < min_iv_ewma_ratio:
                        continue
                    if max_iv_ewma_ratio is not None and iv_ewma_ratio > max_iv_ewma_ratio:
                        continue
                
                # If we reach here, all filters passed
                filtered_data.append(stock)
            
            # Sort the filtered data
            if sort_by in ['symbol', 'iv_current', 'beta_ibov', 'ewma_current', 'close', 'variation', 'iv_ewma_ratio']:
                try:
                    filtered_data.sort(
                        key=lambda x: (
                            x.get(sort_by, '') if sort_by == 'symbol' else 
                            x.get(sort_by, 0) if x.get(sort_by) is not None else 0
                        ),
                        reverse=(sort_order == 'desc')
                    )
                except Exception as e:
                    current_app.logger.error(f"Error sorting data: {str(e)}")
                    # Fall back to symbol sort
                    filtered_data.sort(
                        key=lambda x: x.get('symbol', ''),
                        reverse=(sort_order == 'desc')
                    )
            
            # Apply limit if provided
            if limit and len(filtered_data) > limit:
                filtered_data = filtered_data[:limit]
            
            # Create metadata for the response
            metadata = {
                "total_count": len(filtered_data),
                "filters_applied": {
                    "symbol": symbol,
                    "min_iv_current": min_iv_current,
                    "max_iv_current": max_iv_current,
                    "min_beta_ibov": min_beta_ibov,
                    "max_beta_ibov": max_beta_ibov,
                    "min_iv_ewma_ratio": min_iv_ewma_ratio,
                    "max_iv_ewma_ratio": max_iv_ewma_ratio,
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                    "limit": limit
                }
            }
            
            # Return the filtered and processed data
            return make_response(jsonify({
                "metadata": metadata,
                "results": filtered_data
            }), 200)
            
        except Exception as e:
            current_app.logger.error(f"Error in IBOVStocksResource: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)


class CumulativePerformanceResource(Resource):
    # Cache for cumulative performance data to avoid repeated file operations
    _cache = {
        'data': None,
        'last_updated': None
    }

    def get(self):
        try:
            # Get query parameters
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            assets = request.args.get('assets')  # Comma-separated list of assets to include
            normalize = request.args.get('normalize', 'true').lower() == 'true'  # Normalize to start at 100
            
            # Get the full path to the cumulative_performance_data.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, "utils", "export", "cumulative_performance_data.json")
            
            current_app.logger.info(f"Attempting to read cumulative performance data from: {json_file_path}")
            
            # Check if data is already cached and file hasn't been modified
            file_mtime = os.path.getmtime(json_file_path)
            
            if (self._cache['data'] is None or 
                self._cache['last_updated'] is None or 
                self._cache['last_updated'] < file_mtime):
                
                current_app.logger.info(f"Loading cumulative performance data from file: {json_file_path}")
                
                # Read the JSON file
                with open(json_file_path, 'r') as f:
                    json_data = json.load(f)
                
                # Convert JSON data to DataFrame
                if 'data' in json_data and json_data['data']:
                    df = pd.DataFrame(json_data['data'])
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                else:
                    df = pd.DataFrame()
                
                # Cache the data and update timestamp
                self._cache['data'] = df
                self._cache['json_metadata'] = json_data.get('metadata', {})
                self._cache['last_updated'] = file_mtime
                
                current_app.logger.info(f"Cumulative performance data cached successfully")
            else:
                df = self._cache['data']
                current_app.logger.info(f"Using cached cumulative performance data")
            
            # Filter by date range if provided
            if start_date:
                try:
                    start_dt = pd.to_datetime(start_date)
                    df = df[df.index >= start_dt]
                except Exception as e:
                    current_app.logger.warning(f"Invalid start_date format: {start_date}")
            
            if end_date:
                try:
                    end_dt = pd.to_datetime(end_date)
                    df = df[df.index <= end_dt]
                except Exception as e:
                    current_app.logger.warning(f"Invalid end_date format: {end_date}")
            
            # Filter by assets if provided
            if assets:
                asset_list = [asset.strip() for asset in assets.split(',')]
                # Only keep columns that exist in the dataframe
                available_assets = [asset for asset in asset_list if asset in df.columns]
                if available_assets:
                    df = df[available_assets]
                else:
                    current_app.logger.warning(f"None of the requested assets found: {asset_list}")
            
            # Normalize data to start at 100 if requested
            if normalize and not df.empty:
                # Get the first non-null value for each column as the base
                normalized_df = df.copy()
                for column in df.columns:
                    first_valid_value = df[column].first_valid_index()
                    if first_valid_value is not None:
                        base_value = df.loc[first_valid_value, column]
                        if base_value != 0:
                            normalized_df[column] = (df[column] / base_value) * 100
                df = normalized_df
            
            # Prepare the response data
            data_dict = {
                'dates': df.index.strftime('%Y-%m-%d').tolist(),
                'assets': {}
            }
              # Add each asset's data
            for column in df.columns:
                # Convert NaN values to None for JSON serialization
                column_data = df[column].tolist()
                # Replace NaN values with None
                column_data = [None if pd.isna(x) else x for x in column_data]
                data_dict['assets'][column] = column_data
            
            # Calculate some basic statistics
            date_range = {
                'start_date': df.index.min().strftime('%Y-%m-%d') if not df.empty else None,
                'end_date': df.index.max().strftime('%Y-%m-%d') if not df.empty else None,
                'total_periods': len(df)
            }
            
            # Calculate performance metrics
            performance_metrics = {}
            if not df.empty:
                for column in df.columns:
                    series = df[column].dropna()
                    if not series.empty:
                        performance_metrics[column] = {
                            'total_return': float((series.iloc[-1] / series.iloc[0] - 1) * 100) if len(series) > 1 else 0,
                            'volatility': float(series.pct_change().std() * 100) if len(series) > 1 else 0,
                            'min_value': float(series.min()),
                            'max_value': float(series.max()),
                            'current_value': float(series.iloc[-1]) if not series.empty else None
                        }
            
            # Create metadata
            metadata = {
                'total_assets': len(df.columns),
                'available_assets': list(df.columns),
                'date_range': date_range,
                'normalized': normalize,
                'filters_applied': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'assets': assets
                },
                'performance_metrics': performance_metrics
            }
            
            # Return the data
            return make_response(jsonify({
                'metadata': metadata,
                'data': data_dict
            }), 200)
            
        except Exception as e:
            current_app.logger.error(f"Error in CumulativePerformanceResource: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)

class FluxoDDMResource(Resource):
    def get(self):
        try:
            
            # Get query parameters
            limit = request.args.get('limit', 50, type=int)
            investor_type = request.args.get('investor_type')  # Filter by specific investor type
            
            # Get flux data
            flux_data = get_fluxo_ddm_data()
            
            if not flux_data:
                current_app.logger.error("No flux DDM data available")
                return make_response(jsonify({'error': 'No data available'}), 404)
            
            # Apply investor type filter if provided
            filtered_data = flux_data
            if investor_type and investor_type != 'all':
                # Keep only records where the investor type has meaningful data
                filtered_data = [item for item in flux_data 
                               if isinstance(item, dict) and item.get(investor_type) is not None]
            
            # Apply limit
            if limit and len(filtered_data) > limit:
                filtered_data = filtered_data[:limit]
            
            current_app.logger.info(f"FluxoDDM data successfully retrieved: {len(filtered_data)} records")
            
            return make_response(jsonify({
                'data': filtered_data,
                'metadata': {
                    'total_records': len(flux_data),
                    'filtered_records': len(filtered_data),
                    'investor_types': ['Estrangeiro', 'Institucional', 'PF', 'IF', 'Outros']
                }
            }), 200)
            
        except Exception as e:
            current_app.logger.error(f"Error in FluxoDDMResource: {str(e)}")
            return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)

class DividendCalendarResource(Resource):
    def get(self):
        """
        Get dividend calendar data directly from JSON file
        
        Query Parameters:
        - upcoming_days: Get dividends in next N days (default: 30)
        - payment_date: Specific payment date (DD/MM/YYYY)
        - start_date: Start date filter (DD/MM/YYYY)
        - end_date: End date filter (DD/MM/YYYY)
        - codigo: Filter by stock code
        - tipo: Filter by dividend type
        - min_value: Minimum dividend value filter
        - max_value: Maximum dividend value filter
        - sort_order: Sort order (asc, desc)
        - limit: Maximum number of records to return
        """
        try:
            # Parse query parameters directly from request.args
            upcoming_days = int(request.args.get('upcoming_days', 30))
            payment_date = request.args.get('payment_date')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            codigo = request.args.get('codigo')  # Filter by stock code
            tipo = request.args.get('tipo')  # Filter by dividend type
            min_value = float(request.args.get('min_value')) if request.args.get('min_value') else None
            max_value = float(request.args.get('max_value')) if request.args.get('max_value') else None
            sort_order = request.args.get('sort_order', 'asc')
            limit = int(request.args.get('limit')) if request.args.get('limit') else None
            
            current_app.logger.info(f"DividendCalendar endpoint called with upcoming_days: {upcoming_days}")
            
            # Get the full path to the dividend_calender.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_file_path = os.path.join(base_dir, "utils", "export", "dividend_calender.json")
            
            current_app.logger.info(f"Reading dividend data from: {json_file_path}")
            
            # Read the JSON file directly
            try:
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    raw_data = json.load(file)
            except FileNotFoundError:
                return make_response(jsonify({
                    'error': 'Dividend calendar data file not found'
                }), 404)
            except Exception as e:
                return make_response(jsonify({
                    'error': 'Failed to read dividend calendar data',
                    'message': str(e)
                }), 500)
            
            if not raw_data:
                return make_response(jsonify({
                    'error': 'No dividend calendar data available'
                }), 404)
              # Process and filter the data
            def parse_brazilian_currency(value_str):
                """Parse Brazilian currency format to float"""
                if not value_str or value_str == "":
                    return 0.0
                
                # Convert to string and remove R$ symbol and spaces
                value_str = str(value_str).replace("R$", "").strip()
                
                # If the string is empty after cleaning, return 0
                if not value_str:
                    return 0.0
                
                try:
                    # Handle Brazilian format with comma as decimal separator
                    # Examples: "0,017250", "1.234,56", "1234,56"
                    if "," in value_str:
                        # Split by comma to separate integer and decimal parts
                        parts = value_str.split(",")
                        if len(parts) == 2:
                            # Remove dots from integer part (thousand separators)
                            integer_part = parts[0].replace(".", "")
                            decimal_part = parts[1]
                            # Combine with dot as decimal separator
                            value_str = f"{integer_part}.{decimal_part}"
                        else:
                            # Multiple commas - invalid format
                            return 0.0
                    else:
                        # No comma - check if it's a simple number or has thousand separators
                        if value_str.count(".") > 1:
                            # Multiple dots - thousand separators, remove all dots
                            value_str = value_str.replace(".", "")
                        # If single dot, assume it's decimal separator (keep as is)
                    
                    return float(value_str)
                except (ValueError, AttributeError):
                    current_app.logger.warning(f"Could not parse currency value: {value_str}")
                    return 0.0
            
            today = datetime.now()
            processed_data = []
            
            # Create a set to track unique dates for summary
            unique_dates = set()
            
            for item in raw_data:
                if not item.get('Pagamento'):
                    continue
                
                try:
                    # Parse the payment date
                    payment_date_obj = datetime.strptime(item['Pagamento'], "%d/%m/%Y")
                    
                    # Apply stock code filter
                    if codigo and item.get('Codigo', '').upper() != codigo.upper():
                        continue
                        
                    # Apply dividend type filter
                    if tipo and item.get('Tipo', '').upper() != tipo.upper():
                        continue
                    
                    # Parse actual dividend value for value filters
                    valor_raw = item.get('Valor (R$)', '0')
                    valor_float = parse_brazilian_currency(valor_raw)
                    
                    # Apply value filters
                    if min_value is not None and valor_float < min_value:
                        continue
                    if max_value is not None and valor_float > max_value:
                        continue
                    
                    # Apply date filters
                    if payment_date and item['Pagamento'] != payment_date:
                        continue
                    
                    if start_date:
                        start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")
                        if payment_date_obj < start_date_obj:
                            continue
                    
                    if end_date:
                        end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")
                        if payment_date_obj > end_date_obj:
                            continue
                    
                    # Apply upcoming days filter
                    days_until_payment = (payment_date_obj - today).days
                    if days_until_payment > upcoming_days:
                        continue
                    
                    # Determine status
                    if days_until_payment < 0:
                        status = 'paid'
                    elif days_until_payment == 0:
                        status = 'today'
                    else:
                        status = 'upcoming'
                      # Create enhanced data entry using actual JSON data
                    enhanced_item = {
                        'pagamento': item['Pagamento'],
                        'codigo': item.get('Codigo', 'N/A'),
                        'tipo': item.get('Tipo', 'N/A'),
                        'valor': valor_float,
                        'valor_display': f'R$ {valor_float:.6f}'.replace('.', ',') if valor_float > 0 else 'R$ 0,000000',
                        'registro': item.get('Registro', ''),
                        'ex': item.get('Ex', ''),
                        'days_until_payment': days_until_payment,
                        'status': status,
                        'payment_date_obj': payment_date_obj.isoformat()
                    }
                    
                    processed_data.append(enhanced_item)
                    unique_dates.add(item['Pagamento'])
                    
                except ValueError as e:
                    current_app.logger.warning(f"Invalid date format in item: {item}, error: {e}")
                    continue
            
            # Sort the data
            if sort_order == 'desc':
                processed_data.sort(key=lambda x: x['payment_date_obj'], reverse=True)
            else:
                processed_data.sort(key=lambda x: x['payment_date_obj'])
            
            # Apply limit if provided
            if limit and len(processed_data) > limit:
                processed_data = processed_data[:limit]
            
            # Create summary statistics
            total_value = sum(item['valor'] for item in processed_data)
            companies_count = len(set(item['codigo'] for item in processed_data if item['codigo'] != 'N/A'))
            
            # Group by status for summary
            status_counts = {}
            for item in processed_data:
                status = item['status']
                if status not in status_counts:
                    status_counts[status] = 0
                status_counts[status] += 1
            
            # Group by dividend type for summary
            type_counts = {}
            type_values = {}
            for item in processed_data:
                tipo = item['tipo']
                if tipo not in type_counts:
                    type_counts[tipo] = 0
                    type_values[tipo] = 0
                type_counts[tipo] += 1
                type_values[tipo] += item['valor']
            
            # Prepare response
            response_data = {
                'data': processed_data,                'summary': {
                    'total_records': len(processed_data),
                    'total_value': total_value,
                    'total_value_display': f'R$ {total_value:.2f}'.replace('.', ','),
                    'companies_count': companies_count,
                    'unique_dates': len(unique_dates),
                    'status_breakdown': status_counts,
                    'type_breakdown': {
                        'counts': type_counts,
                        'values': {k: f'R$ {v:.2f}'.replace('.', ',') for k, v in type_values.items()}
                    },
                    'upcoming_days_filter': upcoming_days
                },
                'metadata': {
                    'total_raw_records': len(raw_data),
                    'filtered_records': len(processed_data),
                    'filters_applied': {
                        'upcoming_days': upcoming_days,
                        'payment_date': payment_date,
                        'start_date': start_date,
                        'end_date': end_date,
                        'codigo': codigo,
                        'tipo': tipo,
                        'min_value': min_value,
                        'max_value': max_value
                    },
                    'sorting': {
                        'sort_order': sort_order
                    }
                }
            }
            
            current_app.logger.info(f"DividendCalendar data successfully retrieved: {len(processed_data)} records")
            
            return make_response(jsonify(response_data), 200)
            
        except Exception as e:
            current_app.logger.error(f"Error in DividendCalendar endpoint: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return make_response(jsonify({
                'error': 'Failed to retrieve dividend calendar data',
                'message': str(e)
            }), 500)
