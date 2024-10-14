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

            if response.status_code != 202:
                print(f"Erro na requisição: {response.status_code} - {response.text}")
                return None

            data = response.json()

            if isinstance(data, list) and data:
                data = data[0]

            csv_url = data.get("result", {}).get("url")

            if not csv_url:
                raise Exception("URL do CSV não encontrada na resposta.")

            zip_response = requests.get(csv_url)

            if zip_response.status_code != 200:
                print(
                    f"Erro ao fazer download do arquivo ZIP: {zip_response.status_code}"
                )
                return None

            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as zip_file:
                orders = []
                for filename in zip_file.namelist():
                    with zip_file.open(filename) as csv_file:
                        reader = csv.DictReader(io.TextIOWrapper(csv_file, "utf-8"))
                        for row in reader:
                            if row["status"] == "":
                                orders.append(row)

            if orders:
                self.send_pending_orders_email(orders)

            return orders

        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def send_pending_orders_email(self, orders):
        to_email = os.getenv("NOTIFY_EMAIL")
        subject = "Ordens Pendentes de Aprovação"
        body = f"Foram encontradas as seguintes ordens pendentes:\n\n{orders}"
        self.email_service.send_email(to_email, subject, body)
