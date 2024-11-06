from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
import requests
import logging
from core.services.config_service import ConfigService
from core.services.email_service import EmailService
from core.services.registration_data_service import RegistrationDataService
from core.services.zip_service import ZipService
from utils.search_advisor_email import SearchAdvisorEmail

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Order:
    """Modelo para representar uma ordem."""

    account: str
    symbol: str
    order_qty: str
    order_price: str
    side: str
    holder_name: Optional[str] = None


@dataclass
class AdvisorInfo:
    """Modelo para informações do assessor."""

    email: str
    name: str


class EmailTemplateBuilder:
    """Classe para construção de templates de e-mail."""

    @staticmethod
    def get_email_footer() -> str:
        return (
            "<p style='margin-top: 80px;'></p>"
            "<p style='font-size: 0.8rem'><i><u>Este e-mail é uma mensagem automática e "
            "não deve ser respondida. Qualquer erro percebido ou inconsistência de dados, "
            "além de sugestões e feedbacks, favor contatar o setor de TI da TOP.</u></i></p>"
        )

    @staticmethod
    def build_order_details(order: Order) -> str:
        return (
            f"<p>   - Ativo: {order.symbol} | "
            f"Quantidade: {order.order_qty} | "
            f"Preço: {order.order_price} | "
            f"Lado: {order.side}</p>"
        )

    @classmethod
    def build_consolidated_email(cls, orders_by_client: Dict[str, List[Order]]) -> str:
        body = "<p style='margin-bottom: 50px;'>Foram encontradas as seguintes ordens pendentes:</p>"

        for client, client_orders in orders_by_client.items():
            account_number = client_orders[0].account
            body += f"<p><b>Cliente: {client.title()} (Conta: {account_number})</b></p>"

            for order in client_orders:
                body += cls.build_order_details(order)

        return body + cls.get_email_footer()


class StockOrdersService:
    """Serviço para requisitar e processar ordens de compra e venda."""

    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.email_service = EmailService()
        self.advisor_email_service = SearchAdvisorEmail()
        self.zip_service = ZipService()
        self._base_endpoint = "/iaas-stock-order/api/v1/stock-order"

    def _build_url(self, endpoint: str) -> str:
        """Constrói a URL completa para a requisição."""
        return f"{self.config_service.base_url}{self._base_endpoint}{endpoint}"

    def get_stock_orders(self) -> bool:
        """Requisita ordens da API IaaS Stock Order."""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            url = self._build_url("/orders")

            headers = self.config_service.get_headers()
            response = requests.post(
                url,
                headers=headers,
                json={"startDate": current_date, "endDate": current_date},
                timeout=30,
            )

            if response.status_code == 202:
                logger.info("Requisição aceita. Aguardando webhook para processamento.")
                return True

            logger.error(
                f"Erro na requisição: {response.status_code} - {response.text}"
            )
            return False

        except requests.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return False

    def process_csv_from_url(self, csv_url: str) -> Optional[List[Order]]:
        """Baixa e processa o CSV zipado, retornando ordens pendentes."""
        try:
            zip_response = requests.get(csv_url, timeout=30)
            if zip_response.status_code != 200:
                raise requests.RequestException(
                    f"Erro ao baixar arquivo ZIP: {zip_response.status_code}"
                )

            pending_orders: List[Order] = []
            for reader in self.zip_service.unzip_csv_reader(zip_response):
                for row in reader:
                    if not row.get("ordStatus"):
                        order = self._create_order_from_row(row)
                        pending_orders.append(order)

            return pending_orders

        except Exception as e:
            logger.error(f"Erro ao processar o CSV: {str(e)}")
            return None

    def _create_order_from_row(self, row: Dict[str, Any]) -> Order:
        """Cria um objeto Order a partir de uma linha do CSV."""
        side = "Compra" if row.get("side") == "1" else "Venda"
        order_price = "Mercado" if row.get("price") == "0.0" else row.get("price")
        account = row.get("account", "")

        # Buscar o nome do cliente aqui, antes de criar a ordem
        client_name = self.advisor_email_service.find_client_name_by_account(account)

        return Order(
            account=account,
            symbol=row.get("symbol", ""),
            order_qty=row.get("orderQty", ""),
            order_price=order_price,
            side=side,
            holder_name=client_name,  # Definir o nome do cliente já na criação da ordem
        )

    def send_pending_orders_email(self, orders: List[Order]) -> None:
        """Envia ordens pendentes para a mesa variável e os assessores responsáveis."""
        try:
            self._send_consolidated_email(orders)
            orders_by_advisor = self._group_orders_by_advisor(orders)

            for advisor_email, advisor_orders in orders_by_advisor.items():
                self._send_advisor_email(advisor_email, advisor_orders)

        except Exception as e:
            logger.error(f"Erro ao enviar e-mails: {str(e)}")

    def _send_advisor_email(self, advisor_email: str, orders: List[Order]) -> None:
        """Envia e-mail para o assessor responsável com as ordens pendentes de seus respectivos clientes."""
        if not advisor_email:
            logger.warning(
                "E-mail do assessor não encontrado para as ordens pendentes."
            )
            return

        # Constrói o corpo do e-mail com as ordens pendentes para o assessor
        orders_by_client = self._group_orders_by_client(orders)
        email_body = EmailTemplateBuilder.build_consolidated_email(orders_by_client)

        subject = "Ordens Pendentes de Aprovação dos Seus Clientes"

        # Envia o e-mail
        self.email_service.send_email(advisor_email, subject, email_body, is_html=True)
        logger.info(
            f"E-mail enviado para o assessor {advisor_email} com {len(orders)} ordens pendentes."
        )

    def _group_orders_by_advisor(self, orders: List[Order]) -> Dict[str, List[Order]]:
        """Agrupa as ordens por e-mail do assessor."""
        orders_by_advisor: Dict[str, List[Order]] = {}

        for order in orders:
            _, _, advisor_email, _ = (
                self.advisor_email_service.get_client_and_advisor_info(order.account)
            )

            if advisor_email:
                orders_by_advisor.setdefault(advisor_email, []).append(order)

        return orders_by_advisor

    def _get_advisor_info(self, account: str) -> AdvisorInfo:
        """Obtém informações do assessor para uma conta usando SearchAdvisorEmail."""
        _, advisor_name, advisor_email, _ = (
            self.advisor_email_service.get_client_and_advisor_info(account)
        )

        # if advisor_email == "tatianaguimaraes@topinvgroup.com":
        #     advisor_email = "brunomaia@topinvgroup.com"
        return AdvisorInfo(email=advisor_email, name=advisor_name)

    def _send_consolidated_email(self, orders: List[Order]) -> None:
        """Envia e-mail consolidado para a mesa variável."""
        to_email = os.getenv("NOTIFY_EMAIL")
        if not to_email:
            raise ValueError("E-mail de notificação não configurado")

        orders_by_client = self._group_orders_by_client(orders)
        body = EmailTemplateBuilder.build_consolidated_email(orders_by_client)

        self.email_service.send_email(
            to_email, "Ordens Pendentes de Aprovação", body, is_html=True
        )

    def _group_orders_by_client(self, orders: List[Order]) -> Dict[str, List[Order]]:
        """Agrupa as ordens pendentes por cliente."""
        orders_by_client: Dict[str, List[Order]] = {}
        for order in orders:
            # Usar o holder_name já definido na ordem, com fallback para "Cliente não encontrado"
            holder_name = (
                order.holder_name if order.holder_name else "Cliente não encontrado"
            )
            orders_by_client.setdefault(holder_name, []).append(order)
        return orders_by_client

    def send_empty_pending_orders_email(self) -> None:
        """Envia notificação de que não há ordens pendentes."""
        to_email = os.getenv("NOTIFY_EMAIL")
        if not to_email:
            raise ValueError("E-mail de notificação não configurado")

        body = (
            "<p>Não foram encontradas ordens pendentes.</p>"
            + EmailTemplateBuilder.get_email_footer()
        )

        self.email_service.send_email(
            to_email, "Nenhuma Ordem Pendente de Aprovação", body, is_html=True
        )
