from celery.schedules import crontab

beat_schedule = {
    'run-volatility-analysis': {
        'task': 'app.tasks.run_volatility_analysis',
        'schedule': crontab(minute='*/5', hour='13-21', day_of_week='1-5'),
    },
    'run-covered_call': {
        'task': 'app.tasks.run_covered_call',
        'schedule': crontab(minute='*/5', hour='13-21', day_of_week='1-5'),
    },
    'run-collar': {
        'task': 'app.tasks.run_collar',
        'schedule': crontab(minute='*/5', hour='13-21', day_of_week='1-5'),
    },
    'run-screener-yf': {
        'task': 'app.tasks.run_screener_yf',
        'schedule': crontab(minute='*/5', hour='13-22', day_of_week='1-5'),
    },
    'run-fetch-br-recommendations': {
        'task': 'app.tasks.run_fetch_br_recommendations',
        'schedule': crontab(minute='0', hour='*/4', day_of_week='1-5'),
    },
    'run-yf-historical-90m-60m-15m-5m': {
        'task': 'app.tasks.run_yf_historical_90m_60m_15m_5m',
        'schedule': crontab(minute='*/30', hour='13-22', day_of_week='1-5'),
    },
    'run-yf-historical-1m': {
        'task': 'app.tasks.run_yf_historical_1m',
        'schedule': crontab(minute='0', hour='23', day_of_week='2,5'),
    },
    'run-yf-historical-1w-1d': {
        'task': 'app.tasks.run_yf_historical_1w_1d',
        'schedule': crontab(minute='0', hour='22', day_of_week='1-5'),
    },
}