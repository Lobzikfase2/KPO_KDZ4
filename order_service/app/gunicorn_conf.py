import os

bind = '0.0.0.0:5000'
workers = os.environ.get('ORDER_MS_WORKERS_COUNT')
timeout = 300

order_processing_service_pid = None


def when_ready(server):
    from order_processing import start_order_processing_service
    global order_processing_service_pid
    order_processing_service_pid = start_order_processing_service()


def on_exit(server):
    from order_processing import stop_order_processing_service
    global order_processing_service_pid
    if order_processing_service_pid:
        stop_order_processing_service(order_processing_service_pid)
