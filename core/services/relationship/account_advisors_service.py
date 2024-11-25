from core.services.config_service import ConfigService
import requests
from core.services.zip_service import ZipService


class RelationshipService:
    """Classe para requisitar contas vinculadas do cliente."""

    def __init__(self) -> None:
        self.config_service = ConfigService()

    def get_account_advisors_relationship(self):
        """Requisita contas vinculadas do cliente."""
        endpoint = "/iaas-account-advisor/api/v1/advisor/link/account"
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
        """Realiza o download do CSV zipado e extrai as informações"""
        try:
            zip_response = requests.get(csv_url)
            if zip_response.status_code != 200:
                raise Exception(
                    f"Erro ao baixar o arquivo ZIP: {zip_response.status_code}"
                )

            zip_service = ZipService()

            unziped_file = zip_service.unzip_csv_reader(zip_response)

            relationship_list = []

            for reader in unziped_file:
                for row in reader:
                    account_info = {
                        "customer_account": row.get("account"),
                        "advisor_cge": row.get("sgCGE"),
                    }
                    relationship_list.append(account_info)

            return relationship_list

        except requests.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return None
