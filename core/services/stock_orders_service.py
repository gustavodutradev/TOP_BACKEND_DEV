from core.services.config_service import ConfigService
from core.services.email_service import EmailService
from datetime import datetime
import io
import os
import csv
import zipfile
import requests


class StockOrdersService:
    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.email_service = EmailService()

    def get_stock_orders(self):
        endpoint = f"/iaas-stock-order/api/v1/stock-order/orders"
        url = f"{self.config_service._base_url}{endpoint}"

        start_date = end_date = datetime.now().strftime("%Y-%m-%d")

        try:
            headers = self.config_service.get_headers()
            response = requests.post(
                url,
                headers=headers,
                json={"startDate": start_date, "endDate": end_date},
            )

            if response.status_code == 202:
                print("Requisição aceita. Aguarde o webhook para processamento.")
                return True  # Confirma que a requisição foi aceita

            print(f"Erro na requisição: {response.status_code} - {response.text}")
            return None

        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def send_pending_orders_email(self, orders):
        to_email = os.getenv("NOTIFY_EMAIL")
        subject = "Ordens Pendentes de Aprovação"
        body = f"Foram encontradas as seguintes ordens pendentes:\n\n{orders}"
        self.email_service.send_email(to_email, subject, body)
