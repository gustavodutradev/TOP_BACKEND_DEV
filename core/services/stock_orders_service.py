from core.services.config_service import ConfigService
from core.services.email_service import EmailService
from core.services.registration_data_service import RegistrationDataService
from core.services.zip_service import ZipService
from datetime import datetime
from utils.search_advisor_email import SearchAdvisorEmail
import os
import requests


class StockOrdersService:
    """Classe para requisitar e processar ordens de compra e venda."""

    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.email_service = EmailService()
        self.registration_data_service = RegistrationDataService()
        self.advisor_email_service = SearchAdvisorEmail()
        self.account_cache = {}  # Cache para armazenar informações de contas

    def get_stock_orders(self):
        """Requisita ordens da API IaaS Stock Order."""
        endpoint = "/iaas-stock-order/api/v1/stock-order/orders"
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
        """Baixa e processa o CSV zipado, retornando ordens pendentes."""
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
        """Envia ordens pendentes para a mesa variável e os assessores responsáveis."""
        # Envio consolidado para a mesa variável
        self._send_consolidated_email(orders)

        # Agrupar ordens por assessor e enviar individualmente
        orders_by_advisor = self._group_orders_by_advisor(orders)
        for advisor_email, advisor_orders in orders_by_advisor.items():
            self._send_advisor_email(advisor_email, advisor_orders)

    def _group_orders_by_advisor(self, orders):
        """Agrupa as ordens por e-mail do assessor e nome do cliente."""
        orders_by_advisor = {}
        for order in orders:
            email, name = self.advisor_email_service.get_advisor_info(order["account"])
            holder_name = self.get_account_holder_name(order["account"])

            if not holder_name or holder_name == "Nome não encontrado":
                holder_name = name if name else "Assessor não identificado"

            orders_by_advisor.setdefault(email, []).append(
                {**order, "holder_name": holder_name}
            )

        return orders_by_advisor

    def _send_consolidated_email(self, orders):
        """Envia e-mail consolidado para a mesa variável."""
        to_email = os.getenv("NOTIFY_EMAIL")
        subject = "Ordens Pendentes de Aprovação"

        # Agrupar ordens por cliente
        orders_by_client = self._group_orders_by_client(orders)

        # Construir o corpo do e-mail
        body = "<p>Foram encontradas as seguintes ordens pendentes:</p>"
        for client, client_orders in orders_by_client.items():
            body += f"<p><b>Cliente: {client}</b></p>"
            for order in client_orders:
                body += (
                    f"<p>  - Conta: {order['account']} | Ativo: {order['symbol']} | "
                    f"Quantidade: {order['orderQty']} | Preço: {order['orderPrice']} | Lado: {order['side']}</p>"
                )

        # Enviar o e-mail
        self.email_service.send_email(to_email, subject, body, is_html=True)

    def _group_orders_by_client(self, orders):
        """Agrupa as ordens pendentes por cliente."""
        orders_by_client = {}
        for order in orders:
            holder_name = self.get_account_holder_name(order["account"])
            orders_by_client.setdefault(holder_name, []).append(order)
        return orders_by_client

    def _send_advisor_email(self, advisor_email, orders):
        """Envia e-mail para o assessor responsável com as ordens dos seus clientes."""
        subject = "Ordens Pendentes de Aprovação - Seus Clientes"

        # Agrupar ordens por cliente
        orders_by_client = self._group_orders_by_client(orders)

        # Construir o corpo do e-mail
        body = (
            "<p>Foram encontradas as seguintes ordens pendentes dos seus clientes:</p>"
        )
        for client, client_orders in orders_by_client.items():
            body += f"<p><b>Cliente: {client}</b></p>"
            for order in client_orders:
                body += (
                    f"<p>  - Conta: {order['account']} | Ativo: {order['symbol']} | "
                    f"Quantidade: {order['orderQty']} | Preço: {order['orderPrice']} | Lado: {order['side']}</p>"
                )

        body += "<p>Este e-mail reforça a atenção com as ordens pendentes de seus clientes, para que não perca a atual janela de execução. Favor reforçar aos clientes a necessidade de aprová-las.</p>"

        # Enviar o e-mail para o assessor
        self.email_service.send_email(advisor_email, subject, body, is_html=True)

    def send_empty_pending_orders_email(self):
        """Envia notificação de que não há ordens pendentes."""
        to_email = os.getenv("NOTIFY_EMAIL")
        subject = "Nenhuma Ordem Pendente de Aprovação"
        body = "<p>Não foram encontradas ordens pendentes.</p>"

        self.email_service.send_email(to_email, subject, body, is_html=True)
