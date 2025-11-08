# bot/infra/metrics/prometheus.py

from prometheus_client import Counter, Histogram, Gauge
import time

# RPS (Requests Per Second)
webhook_requests_total = Counter(
    'webhook_requests_total',
    'Total webhook requests',
    ['method', 'endpoint', 'status']
)

webhook_request_duration = Histogram(
    'webhook_request_duration_seconds',
    'Webhook request latency',
    ['endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# Ошибки
bot_errors_total = Counter(
    'bot_errors_total',
    'Total bot errors',
    ['error_type', 'handler']
)

# Размер очереди
queue_size = Gauge(
    'queue_size',
    'Number of jobs in queue',
    ['queue_name']
)

queue_processing_time = Histogram(
    'queue_processing_time_seconds',
    'Time to process job',
    ['queue_name']
)

# БД метрики
db_query_time = Histogram(
    'db_query_time_seconds',
    'Database query time',
    ['query_type']
)

db_pool_active = Gauge(
    'db_pool_active',
    'Active database connections'
)

# Бизнес метрики
users_total = Gauge(
    'users_total',
    'Total users count',
    ['country']
)

auctions_active = Gauge(
    'auctions_active',
    'Active auctions count'
)

purchases_daily = Counter(
    'purchases_daily',
    'Daily purchases',
    ['variant']  # для A/B тестов
)

referral_conversions = Counter(
    'referral_conversions',
    'Referral conversions',
    ['level']  # уровень реферального дерева
)
