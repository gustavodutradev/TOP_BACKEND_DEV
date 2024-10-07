import requests
import json
import os
import uuid
from core.services.token_service import TokenService

class RequestsService:

    def __init__(self) -> None:
        self.token_service = TokenService()
        self.__base_url = "https://api.btgpactual.com"
        self.__uuid = uuid.uuid4()
        self.__token = self.token_service.get_token()

        if not self.__token:
            raise Exception("Token de acesso não disponível.")

        self.__headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'x-id-partner-request': str(self.__uuid),
            'access_token': self.__token
        }
        

    def get_suitability(self, account_number: str):
        endpoint = f"/iaas-suitability/api/v1/suitability/account/{account_number}"
        url = f"{self.__base_url}/{endpoint}"

        print(url)

        try:
            response = requests.get(url, headers=self.__headers)

            # Logando status code e response text
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            # Verifica se a resposta não é 200
            if response.status_code != 200:
                print(f"Erro ao acessar suitability: {response.status_code} - {response.text}")
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
        

    def get_registration_data(self, account_number: str):
        endpoint = f"/iaas-account-management/api/v1/account-management/account/{account_number}/information"
        url = f"{self.__base_url}/{endpoint}"

        print(url)

        try:
            response = requests.get(url, headers=self.__headers)

            # Logando status code e response text
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            # Verifica se a resposta não é 200
            if response.status_code != 200:
                print(f"Erro ao acessar registration data: {response.status_code} - {response.text}")
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


    def get_account_base(self):
        endpoint = "/api-account-base/api/v1/account-base/accounts"
        url = f"{self.__base_url}/{endpoint}"

        print(url)

        try:
            response = requests.get(url, headers=self.__headers)

            # Logando status code e response text
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            # Verifica se a resposta não é 200
            if response.status_code != 200:
                print(f"Erro ao acessar suitability: {response.status_code} - {response.text}")
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
