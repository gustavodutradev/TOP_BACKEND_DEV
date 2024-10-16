from core.services.config_service import ConfigService
from core.services.email_service import EmailService
from datetime import datetime
import io
import os
import csv
import zipfile
import requests


class StockOrdersService:
    """Classe para requisitar ordens de compra e venda."""
    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.email_service = EmailService()

    def get_stock_orders(self):
        """Requisita ordens de compra e venda da API IaaS Stock Order."""
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

    def process_csv_from_url(self, csv_url):
        """Realiza o download do CSV zipado, extrai e filtra ordens pendentes."""
        try:
            # Baixa o arquivo ZIP
            zip_response = requests.get(csv_url)
            if zip_response.status_code != 200:
                raise Exception(
                    f"Erro ao baixar o arquivo ZIP: {zip_response.status_code}"
                )

            pending_orders = []

            # Extrai o conteúdo do ZIP e lê o CSV
            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as zip_file:
                for filename in zip_file.namelist():
                    with zip_file.open(filename) as csv_file:
                        reader = csv.DictReader(io.TextIOWrapper(csv_file, "utf-8"))
                        # Filtra ordens pendentes (status vazio)
                        for row in reader:
                            if row.get("ordStatus", "") == "":

                                side = "Compra" if row.get("side") == "1" else "Venda"
                                order_price = (
                                    "Mercado"
                                    if row.get("price") == "0.0"
                                    else row.get("price")
                                )
                                pending_order = {
                                    "account": row.get("account"),
                                    "symbol": row.get("symbol"),
                                    "orderQty": row.get("orderQty"),
                                    "orderPrice": order_price,
                                    "side": side,
                                }

                                pending_orders.append(pending_order)

            return pending_orders

        except Exception as e:
            print(f"Erro ao processar o CSV: {str(e)}")
            return None

    def send_pending_orders_email(self, orders):
        """Envia as ordens pendentes por e-mail."""
        to_email = os.getenv("NOTIFY_EMAIL")
        subject = "Ordens Pendentes de Aprovação"

        # Formata o corpo do e-mail com as ordens pendentes
        body = "<p>Foram encontradas as seguintes ordens pendentes:</p>"
        for order in orders:
            body += (
                f"<p><b>Conta:</b> {order['account']} | "
                f"<b>Ativo:</b> {order['symbol']} | "
                f"<b>Quantidade:</b> {order['orderQty']} | "
                f"<b>Preço:</b> {order['orderPrice']} | "
                f"<b>Lado:</b> {order['side']}</p>"
            )

        # Envia o e-mail
        self.email_service.send_email(to_email, subject, body, is_html=True)

    def send_empty_pending_orders_email(self):
        """Envia notificação por email alertando que não há ordens pendentes"""
        to_email = os.getenv("NOTIFY_EMAIL")
        subject = "Nenhuma Ordem Pendente de Aprovação"
        body = "<p>Não foram encontradas ordens pendentes.</p>"

        self.email_service.send_email(to_email, subject, body, is_html=True)
