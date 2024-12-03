import requests
import io
import pandas as pd
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.services.config_service import ConfigService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClosedCommissionsService:
    """Classe para requisitar relatório de Fechamento de Comissões dos Assessores"""

    def __init__(self) -> None:
        self.config_service = ConfigService()

    def get_closed_commissions_report(self):
        """Requisita relatório gerencial de Fechamento de Comissões"""
        endpoint = "/api-rm-reports/api/v1/rm-reports/monthly-commission"
        url = f"{self.config_service.base_url}{endpoint}"
        data_atual = datetime.now()

        if data_atual.day <= 7:
            logger.info(
                "Relatório consolidado de comissões do mês anterior disponível após o dia 7 do mês atual."
            )
            ref_date = data_atual - relativedelta(months=2)
        else:
            ref_date = data_atual - relativedelta(months=1)

        # Extrai o mês e o ano do período de referência
        ref_month = ref_date.strftime("%m")
        ref_year = data_atual.strftime("%Y")  # Ano atual

        period = {"refMonth": ref_month, "refYear": ref_year}

        try:
            headers = self.config_service.get_headers()
            response = requests.post(url, json=period, headers=headers)

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
        """Realiza o download do CSV e extrai as informações"""
        try:
            csv_response = requests.get(csv_url)
            if csv_response.status_code != 200:
                raise Exception(
                    f"Erro ao baixar o arquivo CSV: {csv_response.status_code}"
                )

            csv_content = io.StringIO(csv_response.text)
            csv_reader = pd.read_csv(csv_content, delimiter=",")

            data = [row for row in csv_reader]

            return data

        except requests.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return None
