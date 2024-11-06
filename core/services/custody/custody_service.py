from core.services.config_service import ConfigService
import requests
import io
import csv
from datetime import datetime


class CustodyService:
    """Classe para requisitar relatórios de Custódia por Parceiro."""

    def __init__(self) -> None:
        self.config_service = ConfigService()
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
            csv_response = requests.get(csv_url)
            if csv_response.status_code != 200:
                raise Exception(
                    f"Erro ao baixar o arquivo CSV: {csv_response.status_code}"
                )

            csv_content = io.StringIO(csv_response.text.replace('\0', ''))
            csv_reader = csv.DictReader(csv_content, delimiter=",")

            data = [row for row in csv_reader]

            return data

        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return None
