import json
import requests
from core.services.config_service import ConfigService
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PositionsByAccountService:
    def __init__(self):
        self.config_service = ConfigService()

    def get_positions_by_account(self, accountNumber):
        endpoint = f"/iaas-api-position/api/v1/position/{accountNumber}"
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
                        f"Erro ao acessar as posições da conta {accountNumber}: {response.status_code} - {response.text}"
                    )
                return {"error": f"Não há Posições para a conta {accountNumber}"}

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
