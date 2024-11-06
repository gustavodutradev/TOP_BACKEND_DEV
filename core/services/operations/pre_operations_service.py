from core.services.config_service import ConfigService
from core.services.zip_service import ZipService
import requests
import io
import csv


class PreOperationsService:
    """Classe para requisitar relatório de todas Pré-Operações do parceiro"""

    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.zip_service = ZipService()

    def get_pre_operations_report(self):
        """Requisita relatório de todas Pré-Operações do parceiro"""
        endpoint = "/api-pre-operation/api/v1/pre-operation"
        url = f"{self.config_service.base_url}{endpoint}"

        try:
            headers = self.config_service.get_headers()
            response = requests.get(url, headers=headers)

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
                    f"Erro ao baixar o arquivo ZIP: {zip_response.status_code}"
                )
            
            csv_content = self.zip_service.unzip_csv_reader(zip_response)

            csv_reader = csv.DictReader(csv_content, delimiter=",")

            data = [row for row in csv_reader]

            return data

        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return None
