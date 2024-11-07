from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import requests


class PendingOrdersScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone=pytz.timezone("America/Sao_Paulo")
        )
        self._configure_jobs()

    def _configure_jobs(self):
        """Agenda o fluxo de produtos estruturados que estão para vencer"""
        self.scheduler.add_job(self._call_custody_controller, "cron", hour=9, minute=0)
        self.scheduler.start()

    def _call_custody_controller(self):
        """Chama o serviço para verificar e enviar ordens pendentes"""
        print(f"Tarefa disparada em: {datetime.now()}")
        try:
            requests.post(
                "https://topbackenddev-production.up.railway.app/api/v1/custody"
            )
        except requests.RequestException as e:
            print(f"Erro ao chamar o controller: {str(e)}")
            return
