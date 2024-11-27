import json
import requests
from core.services.config_service import ConfigService
# from core.services.zip_service import ZipService
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PositionsByPartnerService:
    def __init__(self):
        self.config_service = ConfigService()

    def get_positions_by_partner(self):
        endpoint = f"/iaas-api-position/api/v1/position/partner"
        url = f"{self.config_service.base_url}{endpoint}"

        try:
            headers = self.config_service.get_headers()

            response = requests.get(url, headers=headers)

            logger.info(response)

            # Logando status code e response text
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            # Verifica se a resposta não é 200
            if response.status_code != 200:
                if response.status_code == 404:
                    print(
                        f"Erro ao acessar as posições do parceiro: {response.status_code} - {response.text}"
                    )
                return {"error": f"Não há posições para o parceiro"}

            # Tentando decodificar a resposta JSON
            response_data = response.json()

            # Verifica se a resposta JSON é válida
            if response_data is None or not isinstance(response_data, dict):
                print("Resposta JSON é nula ou inválida.")
                return {"error": "Nenhum dado retornado."}

            return response_data

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return {"error": str(e)}
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta.")
            return {"error": "Erro ao decodificar a resposta da API."}
        
    # def process_csv_from_url(self, csv_url):
    #     """Realiza o download do CSV zipado e extrai as informações"""
    #     try:
    #         zip_response = requests.get(csv_url)
    #         if zip_response.status_code != 200:
    #             raise Exception(
    #                 f"Erro ao baixar o arquivo ZIP: {zip_response.status_code}"
    #             )
    #         zip_service = ZipService()
    #         unziped_file = zip_service.unzip_csv_reader(zip_response)
    #         wallets_list = []
    #         for reader in unziped_file:
    #             for row in reader:
    #                 wallet = row.get("cod_carteira")
    #                 if wallet:
    #                     wallets_list.append(wallet)
    #         return wallets_list
    #     except requests.RequestException as e:
    #         print(f"Erro na requisição: {str(e)}")
    #         return None