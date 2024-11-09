import json
import requests
from core.services.config_service import ConfigService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LifeInsuranceService:
    def __init__(self):
        self.config_service = ConfigService()

    def get_life_insurance_data(self, accountNumber):
        endpoint = f"/iaas-life-insurance/api/v1/life-insurance/{accountNumber}"
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
                print(
                    f"Erro ao acessar a API de Seguro de Vida: {response.status_code} - {response.text}"
                )
                return {"error": "Falha ao acessar o endpoint."}

            # Tentando decodificar a resposta JSON
            response_data = response.json()

            # Verifica se a resposta JSON é válida
            if response_data is None or not isinstance(response_data, dict):
                print("Resposta JSON é nula ou inválida.")
                return {"error": "Nenhum dado retornado."}

            # Retorna a resposta correta
            return response_data

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return {"error": str(e)}
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta.")
            return {"error": "Erro ao decodificar a resposta da API."}
