from core.services.config_service import ConfigService
from core.services.zip_service import ZipService
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RelationshipService:
    """Classe para requisitar relatório das últimas Operações do parceiro"""

    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.zip_service = ZipService()

    def get_account_advisors_link(self):
        """Requisita relatório de Contas e Assessores responsáveis"""
        endpoint = "/iaas-account-advisor/api/v1/advisor/link/account"
        url = f"{self.config_service.base_url}{endpoint}"

        try:
            headers = self.config_service.get_headers()
            response = requests.get(url, headers=headers)

            logger.info(response)

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

            df = self.zip_service.unzip_and_convert_csv_to_df(zip_response)

            if df is None:
                logger.error("Não foi possível obter o DataFrame")

            logger.info("Dataframe: {df}".format(df))

            return df

        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")