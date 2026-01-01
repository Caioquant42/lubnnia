"""
Main configuration file for the backend API
This file contains configuration settings that are used throughout the application
"""
import os

class Config:
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # API settings - should match the frontend configuration
    API_VERSION = 'v1'
    API_PREFIX = '/api'
    
    # CORS settings - list of allowed origins
    ALLOWED_ORIGINS = ['http://localhost:3000', 'https://zommaquant.com.br']
      # Celery and Redis settings
    broker_url = 'redis://localhost:6379/0'
    RESULT_BACKEND = 'redis://localhost:6379/0'
    # Keep the old keys for backwards compatibility
    CELERY_broker_url = broker_url
    result_backend = RESULT_BACKEND
    beat_schedule = {}  # Empty beat schedule - can be configured elsewhere if needed
    broker_connection_retry_on_startup = True
    timezone = 'America/Sao_Paulo'  # Set timezone for beat schedule
      # API endpoint paths - should match frontend apiPaths in config.ts
    API_PATHS = {
        'rrg': '/rrg',
        'br_recommendations': '/br-recommendations',
        'screener_rsi': '/screener-rsi',
        'volatility_surface': '/volatility-surface',
        'collar': '/collar',
        'covered_call': '/covered-call',
        'pairs_trading': '/pairs-trading',
        'ibov_stocks': '/ibov-stocks',
        'cumulative_performance': '/cumulative-performance',
        'fluxo_ddm': '/fluxo-ddm',
        'dividend_calendar': '/dividend-calendar',
    }