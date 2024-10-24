from core.services.config_service import ConfigService
from core.services.email_service import EmailService
from core.services.registration_data_service import RegistrationDataService
from core.services.zip_service import ZipService
from datetime import datetime
import os
import requests


class StockOrdersService:
    """Classe para requisitar ordens de compra e venda."""

    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.email_service = EmailService()
        self.registration_data_service = RegistrationDataService()
        self.account_cache = {}  # Cache para armazenar informações de contas

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
                return True

            print(f"Erro na requisição: {response.status_code} - {response.text}")
            return None

        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def process_csv_from_url(self, csv_url):
        """Realiza o download do CSV zipado e extrai ordens pendentes."""
        try:
            zip_response = requests.get(csv_url)
            if zip_response.status_code != 200:
                raise Exception(
                    f"Erro ao baixar o arquivo ZIP: {zip_response.status_code}"
                )

            zip_service = ZipService()
            pending_orders = []

            for reader in zip_service.unzip_csv_reader(zip_response):
                for row in reader:
                    if row.get("ordStatus", "") == "":
                        side = "Compra" if row.get("side") == "1" else "Venda"
                        order_price = (
                            "Mercado" if row.get("price") == "0.0" else row.get("price")
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

    def get_account_holder_name(self, account_number: str) -> str:
        """Busca o nome do titular da conta com cache."""
        if account_number in self.account_cache:
            return self.account_cache[account_number]

        holder_name = self.registration_data_service.get_holder_name(account_number)
        self.account_cache[account_number] = holder_name
        return holder_name

    def send_pending_orders_email(self, orders):
        """Envia as ordens pendentes por e-mail, agrupadas e ordenadas por cliente."""
        to_email = os.getenv("NOTIFY_EMAIL")
        subject = "Ordens Pendentes de Aprovação"

        # Agrupar ordens por cliente em um dicionário
        orders_by_client = {}
        for order in orders:
            holder_name = self.get_account_holder_name(order["account"])
            orders_by_client.setdefault(holder_name, []).append(order)

        # Ordenar os clientes alfabeticamente
        sorted_clients = sorted(orders_by_client.keys())

        # Construir o corpo do email com as ordens agrupadas e ordenadas
        body = "<p>Foram encontradas as seguintes ordens pendentes:</p>"
        for client in sorted_clients:
            body += f"<p><b>Cliente: {client}</b></p>"
            for order in orders_by_client[client]:
                body += (
                    f"<p>  - Conta: {order['account']} | Ativo: {order['symbol']} | "
                    f"Quantidade: {order['orderQty']} | Preço: {order['orderPrice']} | Lado: {order['side']}</p>"
                )

        # Enviar o email
        self.email_service.send_email(to_email, subject, body, is_html=True)

    # def send_pending_orders_email(self, orders):
    #     """Envia as ordens pendentes por e-mail, ordenadas alfabeticamente pelo nome dos clientes."""
    #     to_email = os.getenv("NOTIFY_EMAIL")
    #     subject = "Ordens Pendentes de Aprovação"

    #     # Adicionar nomes dos clientes às ordens para facilitar a ordenação.
    #     enriched_orders = []
    #     for order in orders:
    #         account_number = order["account"]
    #         holder_name = self.get_account_holder_name(
    #             account_number
    #         )  # Obtemos o nome do cliente.

    #         # Enriquecer a ordem com o nome do cliente.
    #         order_with_name = {**order, "holder_name": holder_name}
    #         enriched_orders.append(order_with_name)

    #     # Ordenar as ordens alfabeticamente pelo nome do cliente (holder_name).
    #     enriched_orders.sort(key=lambda x: x["holder_name"])

    #     # Construir o corpo do e-mail com a lista ordenada.
    #     body = "<p>Foram encontradas as seguintes ordens pendentes:</p>"
    #     for order in enriched_orders:
    #         body += (
    #             f"<p><b>Cliente:</b> {order['holder_name']} | "
    #             f"<b>Conta:</b> {order['account']} | "
    #             f"<b>Ativo:</b> {order['symbol']} | "
    #             f"<b>Quantidade:</b> {order['orderQty']} | "
    #             f"<b>Preço:</b> {order['orderPrice']} | "
    #             f"<b>Lado:</b> {order['side']}</p>"
    #         )

    #     # Enviar o e-mail.
    #     self.email_service.send_email(to_email, subject, body, is_html=True)

    def send_empty_pending_orders_email(self):
        """Envia notificação por email alertando que não há ordens pendentes."""
        to_email = os.getenv("NOTIFY_EMAIL")
        subject = "Nenhuma Ordem Pendente de Aprovação"
        body = "<p>Não foram encontradas ordens pendentes.</p>"

        self.email_service.send_email(to_email, subject, body, is_html=True)
