import os
from random import randint
from time import sleep

from config import app, logger, cooking_time_min, cooking_time_max
from db_api.db_funcs import get_waiting_order, update_order_status


def order_processing_service():
    with app.app_context():
        while True:
            order = get_waiting_order()
            if order:
                logger.info(f"Начинаю готовить заказ {order.id}")
                update_order_status(order.id, "cooking")
                sleep(randint(cooking_time_min, cooking_time_max))
                update_order_status(order.id, "completed")
                logger.info(f"Заказ {order.id} был приготовлен")
            sleep(5)


def start_order_processing_service():
    logger.info("Starting order processing service...")
    if (pid := os.fork()) == 0:
        logger.info("Order processing service was started successfully")
        order_processing_service()
    elif pid != -1:
        return pid


def stop_order_processing_service(pid):
    logger.info("Stopping order processing service...")
    os.kill(pid, 9)
    os.waitpid(pid, 0)
    logger.info("Order processing service was stopped successfully")
