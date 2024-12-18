from typing import Dict
from core.services.config_service import ConfigService
from core.services.zip_service import ZipService
from core.services.email_service import EmailService
from utils.map_client_advisor_info import AdvisorLookup
import requests
from datetime import datetime, timedelta
import logging
import os

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustodyService:
    """Classe para requisitar relatórios de Custódia e envio de notificações sobre vencimento de produtos estruturados."""

    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.zip_service = ZipService()
        self.email_service = EmailService()
        self.map_service = AdvisorLookup()
        self.endpoint = "/api-partner-report-extractor/api/v1/report"

    def get_custody(self):
        """Requisita relatório de Custódia por Parceiro"""
        url = f"{self.config_service.base_url}{self.endpoint}/custody"
        try:
            headers = self.config_service.get_headers()
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 202:
                logger.info("Requisição aceita. Aguarde o webhook para processamento.")
                return True
            logger.error(
                f"Erro na requisição: {response.status_code} - {response.text}"
            )
            return None
        except requests.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return None

    def process_csv_from_url(self, csv_url):
        """Realiza o download do CSV, converte para DataFrame e extrai as informações"""
        try:
            zip_response = requests.get(csv_url, timeout=30)
            if zip_response.status_code != 200:
                raise requests.RequestException(
                    f"Erro ao baixar arquivo ZIP: {zip_response.status_code}"
                )

            # Utiliza o novo método para descompactar o ZIP e obter o DataFrame
            df = self.zip_service.unzip_and_convert_csv_to_df(zip_response)
            if df is None:
                return []

            # Converte a coluna "fixingDate" para o formato dd/mm/aaaa
            if "fixingDate" in df.columns:
                df["fixingDate"] = df["fixingDate"].apply(
                    lambda x: (
                        self.convert_excel_date(x)
                        if isinstance(x, (int, float))
                        else str(x)
                    )
                )

            # Converte o DataFrame em uma lista de dicionários
            data = df.to_dict(orient="records")
            return data

        except Exception as e:
            logger.error(f"Erro ao processar o CSV: {str(e)}")
            return []

    def convert_excel_date(self, serial):
        """Converte uma data serial do Excel para o formato dd/mm/aaaa."""
        base_date = datetime(1899, 12, 30)  # Data de base do Excel
        converted_date = base_date + timedelta(days=serial)
        return converted_date.strftime("%d/%m/%Y")

    def _filter_products_to_expire(self, data):
        """Filtra produtos com vencimento para a data de hoje."""
        today = datetime.now().strftime(
            "%d/%m/%Y"
        )  # Obtém a data de hoje no formato dd/mm/aaaa
        expiring_products = []
        for row in data:
            try:
                # Converte a data de vencimento do produto, assumindo que ela esteja no formato dd/mm/aaaa
                fixing_date = datetime.strptime(row["fixingDate"], "%d/%m/%Y").strftime(
                    "%d/%m/%Y"
                )
                if fixing_date == today:
                    expiring_products.append(row)
            except ValueError as e:
                logger.error(
                    f"Erro ao converter a data de vencimento para o produto {row}: {e}"
                )
        return expiring_products

    def _consolidate_operations(self, products):
        """Consolida operações duplicadas de PUT e CALL para o mesmo cliente e ativo."""
        consolidated_products = []
        seen_operations = set()
        for product in products:
            # Usa get com valor padrão caso a chave não exista
            key = (
                product.get("accountNumber"),
                product.get("referenceAsset"),
                product.get("nomeDoProduto"),
                product.get(
                    "qtdAtual", 0
                ),  # Valor padrão de 0 para qtdAtual caso não exista
            )
            if key not in seen_operations:
                seen_operations.add(key)
                consolidated_products.append(product)
        return consolidated_products

    def _group_by_client(self, data):
        """Agrupa produtos por cliente, considerando accountNumber como chave e dados do cliente como valor."""
        grouped_data = {}
        for row in data:
            account_number = row.get("accountNumber")
            if not account_number:
                logger.warning(f"Produto sem 'accountNumber': {row}")
                continue

            # Agrupa os produtos pelo número da conta e garante que as informações do cliente estejam no formato esperado
            if account_number not in grouped_data:
                grouped_data[account_number] = {
                    "accountName": row.get("accountName", "Nome não disponível"),
                    "accountNumber": account_number,
                    "products": [],
                }

            grouped_data[account_number]["products"].append(row)

        return grouped_data

    def send_email_to_variable_desk(self, expiring_products):
        """Envia e-mail para a Mesa de Renda Variável com todos os produtos para vencimento."""
        subject = f"Produtos Estruturados para Vencimento - {datetime.now().strftime('%d/%m/%Y')}"
        body = "Prezada Mesa Variável, foram encontrados produtos estruturados com vencimento para a data de hoje:\n\n"

        grouped_by_client = self._group_by_client(expiring_products)
        for client, client_data in grouped_by_client.items():
            account_name = client_data.get("accountName", "Nome não disponível")
            body += f"<p><b>Cliente: {account_name.title()} (Conta: {client_data['accountNumber']})</b></p>"
            for product in client_data["products"]:
                body += (
                    f"<p>Ativo: {product['referenceAsset']} | "
                    f"Produto: {product['nomeDoProduto']}</p>"
                )

        to_email = os.getenv("NOTIFY_EMAIL")
        body += self.get_email_footer()
        self.email_service.send_email(to_email, subject, body, is_html=True)
        logger.info("E-mail consolidado enviado para a mesa de renda variável")

    def _group_products_by_advisor(self, expiring_products: list) -> Dict[str, list]:
        """
        Group the expiring products by advisor email.
        Args:
            expiring_products: List of products with expiration details
        Returns:
            A dictionary with advisor emails as keys and lists of products as values
        """
        products_by_advisor = {}

        for product in expiring_products:
            advisor_info = self.map_service.get_advisor_info(product["accountNumber"])

            if not advisor_info:
                logger.error("Não foi possível coletar as informações do assessor.")

            advisor_name = advisor_info.get("advisorName")
            advisor_email = advisor_info.get("email")

            # Verificar se todos os valores necessários estão presentes
            if advisor_name is None or advisor_email is None:
                logger.error(
                    f"Assessor ou e-mail não encontrado para a conta {product['accountNumber']}."
                )
                continue  # Pula este produto se não encontrar dados do assessor

            # Adicionar o produto ao grupo de assessores
            if advisor_email not in products_by_advisor:
                products_by_advisor[advisor_email] = {
                    "avisor_name": advisor_name,
                    "products": [],
                }
            products_by_advisor[advisor_email]["products"].append(product)

        return products_by_advisor

    def send_email_to_advisors(self, expiring_products):
        """Envia e-mails para os assessores com produtos de seus clientes que estão para vencer"""
        products_by_advisor = self._group_products_by_advisor(expiring_products)
        for advisor_email, advisor_data in products_by_advisor.items():
            advisor_name = advisor_data["avisor_name"]
            products = advisor_data["products"]

            subject = f"Produtos Estruturados para Vencimento - {datetime.now().strftime('%d/%m/%Y')}"
            body = f"Prezado(a) {advisor_name}, abaixo encontram-se produtos estruturados de seus clientes com vencimento para data de hoje:\n\n"

            grouped_by_client = self._group_by_client(products)
            for client, client_data in grouped_by_client.items():
                body += f"<p><b>Cliente: {client_data['accountName'].title()} (Conta: {client_data['accountNumber']})</b></p>"
                for product in client_data["products"]:
                    body += (
                        f"<p>Ativo: {product['referenceAsset']} | "
                        f"Produto: {product['nomeDoProduto']}</p>"
                    )
            body += self.get_email_footer()
            self.email_service.send_email(advisor_email, subject, body, is_html=True)
            logger.info(f"E-mail enviado para o assessor {advisor_email}")

    def execute_daily_expiration_check(self, csv_url):
        """Executa a verificação de produtos para vencimento e envia e-mails conforme necessário"""
        data = self.process_csv_from_url(csv_url)

        if not data:
            logger.error("Nenhum dado foi extraído do arquivo CSV.")
            return

        expiring_products = self._filter_products_to_expire(data)

        if not expiring_products:
            self.send_empty_products_to_expire_email()
            return

        # Consolidando as operações antes de enviar os e-mails
        consolidated_products = self._consolidate_operations(expiring_products)
        self.send_email_to_variable_desk(consolidated_products)
        self.send_email_to_advisors(consolidated_products)

    def get_email_footer(self) -> str:
        return (
            "<p style='margin-top: 80px;'></p>"
            "<p style='font-size: 0.8rem'><i><u>Este e-mail é uma mensagem automática e "
            "não deve ser respondida. Qualquer erro percebido ou inconsistência de dados, "
            "além de sugestões e feedbacks, favor contatar o setor de TI da TOP.</u></i></p>"
        )

    def send_empty_products_to_expire_email(self) -> None:
        """Envia notificação de que não há produtos estruturados para vencer no dia corrente."""
        to_email = os.getenv("NOTIFY_EMAIL")
        if not to_email:
            raise ValueError("E-mail de notificação não configurado")

        body = (
            "<p>Não há produtos estruturados com vencimento para a data de hoje.</p>"
            + self.get_email_footer()
        )

        self.email_service.send_email(
            to_email,
            f"Não há produtos Estruturados para Vencimento - {datetime.now().strftime('%d/%m/%Y')}",
            body,
            is_html=True,
        )
