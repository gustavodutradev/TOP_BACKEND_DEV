from core.services.config_service import ConfigService
import json
import requests


class RegistrationDataService(ConfigService):
    def __init__(self) -> None:
        self.config_service = ConfigService()

    def get_registration_data(self, account_number: str):
        endpoint = f"/iaas-account-management/api/v1/account-management/account/{account_number}/information"
        url = f"{self.config_service._base_url}{endpoint}"

        print(url)

        try:
            headers = self.config_service.get_headers()

            response = requests.get(url, headers=headers)

            # Logando status code e response text
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            # Verifica se a resposta não é 200
            if response.status_code != 200:
                print(
                    f"Erro ao acessar suitability: {response.status_code} - {response.text}"
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
