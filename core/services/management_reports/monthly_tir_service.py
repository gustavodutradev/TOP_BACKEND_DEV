from core.services.config_service import ConfigService
import requests
import io
import csv
from urllib.parse import urlparse

class MonthlyTIRReportService:
    """Classe para requisitar Relatório Gerencial de TIR mensal."""

    def __init__(self) -> None:
        self.config_service = ConfigService()

    def get_monthly_tir_report(self):
        """Requisita relatório gerencial de TIR mensal"""
        endpoint = "/api-rm-reports/api/v1/rm-reports/monthly-tir"
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

    def validate_url(self, url):
        """Valida se a URL possui um esquema válido e está bem formada"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def process_csv_from_url(self, csv_url):
        """Realiza o download do CSV e extrai as informações"""
        try:
            # Valida a URL antes de fazer a requisição
            if not csv_url or not self.validate_url(csv_url):
                raise ValueError(f"URL inválida ou mal formatada: {csv_url}")

            csv_response = requests.get(csv_url)
            if csv_response.status_code != 200:
                raise Exception(
                    f"Erro ao baixar o arquivo CSV: {csv_response.status_code}"
                )

            csv_content = io.StringIO(csv_response.text)
            csv_reader = csv.DictReader(csv_content, delimiter=",")

            data = [row for row in csv_reader]

            return data

        except ValueError as e:
            print(f"Erro de validação da URL: {str(e)}")
            return None
        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return None