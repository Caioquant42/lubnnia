import subprocess
from celery import shared_task

@shared_task
def run_fetch_br_recommendations():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/app/utils/all_BR_recommendations.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "BR recommendations Analysis script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing BR recommendations Analysis script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing BR recommendations Analysis script: {e}"


@shared_task
def run_fetch_agenda_dividendos():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/app/utils/dividend_calender.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "Agenda Analysis script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing Agenda Analysis script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing Agenda Analysis script: {e}"

@shared_task
def run_screener_yf():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/app/utils/screener_yf.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "screener_yf Analysis script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing screener_yf Analysis script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing screener_yf Analysis script: {e}"

@shared_task
def run_rrg_data():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/app/utils/rrg_data.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "rrg_data Analysis script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing rrg_data Analysis script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing rrg_data Analysis script: {e}"

@shared_task
def run_covered_call():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/app/utils/covered_call.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "covered_call Analysis script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing covered_call Analysis script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing covered_call Analysis script: {e}"

@shared_task
def run_collar():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/app/utils/collar.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "collar Analysis script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing collar Analysis script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing collar Analysis script: {e}"



@shared_task
def run_volatility_analysis():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/app/utils/volatility_analysis.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "Volatility Analysis script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing Volatility Analysis script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing Volatility Analysis script: {e}"


@shared_task
def run_cointegration_matrix():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/app/utils/cointegration_matrix.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "Fetch cointegration_matrix script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing fetch cointegration_matrix script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing fetch cointegration_matrix script: {e}"



###################################################################################################################################
###################################### DOLPHINDB TASKS ############################################################################
###################################################################################################################################


@shared_task
def run_yf_historical_90m_60m_15m_5m():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/dolphindb/yfs/historical_90m_60m_15m_5m.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "Fetch Yahoo Finance historical_90m_60m_15m_5m script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing fetch Yahoo Finance historical_90m_60m_15m_5m script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing fetch Yahoo Finance historical_90m_60m_15m_5m script: {e}"

@shared_task
def run_yf_historical_1m():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/dolphindb/yfs/historical_1m.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "Fetch Yahoo Finance historical_1m script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing fetch Yahoo Finance historical_1m script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing fetch Yahoo Finance historical_1m script: {e}"

@shared_task
def run_yf_historical_1w_1d():
    try:
        result = subprocess.run([
            '/var/www/next/next2/project_mvp/backend/backenv/bin/python',
            '/var/www/next/next2/project_mvp/backend/dolphindb/yfs/historical_1w_1d.py'
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return "Fetch Yahoo Finance historical_1w_1d script executed successfully"
    except subprocess.CalledProcessError as e:
        print(f"Error executing fetch Yahoo Finance historical_1w_1d script: {e}")
        print(f"Script output: {e.output}")
        return f"Error executing fetch Yahoo Finance historical_1w_1d script: {e}"
