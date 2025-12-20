import os
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

def str_to_float_value(s):
    """Convert Brazilian currency string to float value"""
    if isinstance(s, (int, float)):
        return float(s)
    
    if not isinstance(s, str):
        return 0.0
        
    # Remove currency symbols and convert comma to dot
    s = s.replace("R$", "").replace(" ", "").strip()
    s = s.replace(",", ".")
    
    try:
        return float(s)
    except ValueError:
        return 0.0

def parse_date(date_string: str) -> Optional[datetime]:
    """Parse DD/MM/YYYY date string to datetime object"""
    if not date_string:
        return None
    
    try:
        return datetime.strptime(date_string, "%d/%m/%Y")
    except ValueError:
        return None

def format_date_for_display(date_string: str) -> str:
    """Format date string for display"""
    parsed_date = parse_date(date_string)
    if parsed_date:
        return parsed_date.strftime("%d/%m/%Y")
    return date_string

def get_dividend_calendar_data():
    """Get dividend calendar data from local JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "export", "dividend_calender.json")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        print(f"Successfully read dividend calendar data: {len(data)} entries loaded")
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return []
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        return []

def process_dividend_data(data: List[Dict], 
                         codigo: Optional[str] = None,
                         tipo: Optional[str] = None,
                         min_value: Optional[float] = None,
                         max_value: Optional[float] = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         payment_date: Optional[str] = None,
                         sort_by: str = 'Pagamento',
                         sort_order: str = 'asc',
                         limit: Optional[int] = None) -> List[Dict]:
    """Process and filter dividend calendar data"""
    
    processed_data = []
    
    for item in data:
        # Skip items that don't have required fields or are incomplete
        if not item.get('Pagamento'):
            continue
            
        # Convert value to float for processing
        valor_str = item.get('Valor (R$)', '0')
        valor_float = str_to_float_value(valor_str)
        
        # Create processed item
        processed_item = {
            'codigo': item.get('Codigo', ''),
            'tipo': item.get('Tipo', ''),
            'valor_brl': valor_str,
            'valor_numeric': valor_float,
            'registro': item.get('Registro', ''),
            'ex': item.get('Ex', ''),
            'pagamento': item.get('Pagamento', '')
        }
        
        # Apply filters
        if codigo and processed_item['codigo'].upper() != codigo.upper():
            continue
            
        if tipo and processed_item['tipo'].upper() != tipo.upper():
            continue
            
        if min_value is not None and valor_float < min_value:
            continue
            
        if max_value is not None and valor_float > max_value:
            continue
            
        # Date filters
        if start_date:
            payment_datetime = parse_date(processed_item['pagamento'])
            start_datetime = parse_date(start_date)
            if payment_datetime and start_datetime and payment_datetime < start_datetime:
                continue
                
        if end_date:
            payment_datetime = parse_date(processed_item['pagamento'])
            end_datetime = parse_date(end_date)
            if payment_datetime and end_datetime and payment_datetime > end_datetime:
                continue
                
        if payment_date:
            if processed_item['pagamento'] != payment_date:
                continue
        
        processed_data.append(processed_item)
    
    # Sort data
    if sort_by in ['codigo', 'tipo', 'valor_numeric', 'registro', 'ex', 'pagamento']:
        reverse = sort_order.lower() == 'desc'
        
        if sort_by in ['registro', 'ex', 'pagamento']:
            # Sort by date
            processed_data.sort(
                key=lambda x: parse_date(x[sort_by]) or datetime.min,
                reverse=reverse
            )
        elif sort_by == 'valor_numeric':
            processed_data.sort(key=lambda x: x['valor_numeric'], reverse=reverse)
        else:
            processed_data.sort(key=lambda x: x[sort_by], reverse=reverse)
    
    # Apply limit
    if limit and len(processed_data) > limit:
        processed_data = processed_data[:limit]
    
    return processed_data

def get_dividend_summary(data: List[Dict]) -> Dict:
    """Generate summary statistics for dividend data"""
    if not data:
        return {
            'total_entries': 0,
            'unique_stocks': 0,
            'total_value': 0.0,
            'avg_value': 0.0,
            'dividend_count': 0,
            'jcp_count': 0,
            'upcoming_payments': 0
        }
    
    # Calculate statistics
    total_entries = len(data)
    unique_stocks = len(set(item['codigo'] for item in data if item['codigo']))
    
    values = [item['valor_numeric'] for item in data if item['valor_numeric'] > 0]
    total_value = sum(values)
    avg_value = total_value / len(values) if values else 0.0
    
    dividend_count = sum(1 for item in data if item['tipo'].upper() == 'DIVIDENDO')
    jcp_count = sum(1 for item in data if item['tipo'].upper() == 'JCP')
    
    # Count upcoming payments (from today)
    today = datetime.now()
    upcoming_payments = 0
    for item in data:
        payment_date = parse_date(item['pagamento'])
        if payment_date and payment_date >= today:
            upcoming_payments += 1
    
    return {
        'total_entries': total_entries,
        'unique_stocks': unique_stocks,
        'total_value': round(total_value, 2),
        'avg_value': round(avg_value, 4),
        'dividend_count': dividend_count,
        'jcp_count': jcp_count,
        'upcoming_payments': upcoming_payments
    }

def get_dividend_by_stock(data: List[Dict], codigo: str) -> List[Dict]:
    """Get all dividend entries for a specific stock"""
    return [item for item in data if item.get('codigo', '').upper() == codigo.upper()]

def get_upcoming_dividends(data: List[Dict], days_ahead: int = 30) -> List[Dict]:
    """Get dividends with payment dates in the next N days"""
    from datetime import timedelta
    today = datetime.now()
    cutoff_date = datetime(today.year, today.month, today.day) + timedelta(days=days_ahead)
    
    upcoming = []
    for item in data:
        payment_date = parse_date(item['pagamento'])
        if payment_date and today <= payment_date <= cutoff_date:
            upcoming.append(item)
    
    return sorted(upcoming, key=lambda x: parse_date(x['pagamento']) or datetime.min)
