from core.services.config_service import ConfigService
import requests
import io
import csv


class PositionReportService:
    """Classe para requisitar Relatório Gerencial de Posições."""

    def __init__(self) -> None:
        self.config_service = ConfigService()

    def get_positions_report(self):
        """Requisita relatório gerencial de Posições"""
        endpoint = "/api-rm-reports/api/v1/rm-reports/position"
        url = f"{self.config_service._base_url}{endpoint}"

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
            csv_response = requests.get(csv_url)
            if csv_response.status_code != 200:
                raise Exception(
                    f"Erro ao baixar o arquivo CSV: {csv_response.status_code}"
                )

            csv_content = io.StringIO(csv_response.text)
            csv_reader = csv.DictReader(csv_content, delimiter=",")

            data = [row for row in csv_reader]

            return data

        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return None
