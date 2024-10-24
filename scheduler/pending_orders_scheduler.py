from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import requests
import os


class PendingOrdersScheduler:
    def __init__(self):
        if os.getenv("GUNICORN_WORKER_ID") is None:
            self.scheduler = BackgroundScheduler(
                timezone=pytz.timezone("America/Sao_Paulo")
            )
            self._configure_jobs()

    def _configure_jobs(self):
        """Agenda o fluxo de ordens pendentes"""
        self.scheduler.add_job(self._call_orders_controller, "cron", hour=11, minute=30)
        self.scheduler.add_job(self._call_orders_controller, "cron", hour=16, minute=0)
        self.scheduler.start()

    def _call_orders_controller(self):
        """Chama o serviço para verificar e enviar ordens pendentes"""
        print(f"Tarefa disparada em: {datetime.now()}")
        try:
            requests.post(
                "https://topbackenddev-production.up.railway.app/api/v1/orders"
            )
        except requests.RequestException as e:
            print(f"Erro ao chamar o controller: {str(e)}")
            return
