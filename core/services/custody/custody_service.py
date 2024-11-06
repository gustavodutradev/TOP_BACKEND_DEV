from core.services.config_service import ConfigService
from core.services.zip_service import ZipService
import requests
import io
import csv
from datetime import datetime
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustodyService:
    """Classe para requisitar relatórios de Custódia por Parceiro."""

    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.zip_service = ZipService()
        self.endpoint = "/api-partner-report-extractor/api/v1/report"

    def get_custody(self):
        """Requisita relatório de Custódia por Parceiro"""
        url = f"{self.config_service.base_url}{self.endpoint}/custody"

        try:
            headers = self.config_service.get_headers()
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 202:
                print("Requisição aceita. Aguarde o webhook para processamento.")
                return True

            print(f"Erro na requisição: {response.status_code} - {response.text}")
            return None

        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def get_custody_by_date(self):
        """Requisita relatório de Custódia por Data"""
        url = f"{self.config_service.base_url}{self.endpoint}/custody-by-date"
        current_date = datetime.now().strftime("%Y-%m-%d")

        try:
            headers = self.config_service.get_headers()
            response = requests.post(
                url, headers=headers, json={"refDate": current_date}, timeout=30
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
        """Realiza o download do CSV e extrai as informações"""
        try:
            zip_response = requests.get(csv_url, timeout=30)
            if zip_response.status_code != 200:
                raise requests.RequestException(
                    f"Erro ao baixar arquivo ZIP: {zip_response.status_code}"
                )

            csv_readers = self.zip_service.unzip_csv_reader(zip_response)
            if csv_readers is None:
                return []

            data = []
            for csv_reader in csv_readers:
                data.extend([row for row in csv_reader])

            return data

        except Exception as e:
            logger.error(f"Erro ao processar o CSV: {str(e)}")
            return []
