from core.services.config_service import ConfigService
import json
import requests


class RegistrationDataService:
    """Serviço para acessar dados cadastrais de contas."""

    def __init__(self) -> None:
        self.config_service = ConfigService()

    def get_registration_data(self, account_number: str):
        """Busca todos os dados cadastrais de uma conta."""
        endpoint = f"/iaas-account-management/api/v1/account-management/account/{account_number}/information"
        url = f"{self.config_service._base_url}{endpoint}"
        print(f"URL: {url}")

        try:
            headers = self.config_service.get_headers()
            response = requests.get(url, headers=headers)

            # Logando status code e response
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code != 200:
                print(
                    f"Erro ao acessar dados: {response.status_code} - {response.text}"
                )
                return {"error": "Falha ao acessar o endpoint."}

            response_data = response.json()
            if not isinstance(response_data, dict):
                print("Resposta JSON é inválida.")
                return {"error": "Resposta inválida da API."}

            return response_data

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return {"error": str(e)}
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON.")
            return {"error": "Erro ao decodificar a resposta da API."}

    def get_holder_name(self, account_number: str) -> str:
        """Busca apenas o nome do titular de uma conta."""
        registration_data = self.get_registration_data(account_number)

        if "error" in registration_data:
            print(f"Erro ao buscar nome do titular: {registration_data['error']}")
            return "Nome não encontrado"

        try:
            holder_name = registration_data["holder"]["name"]
            return holder_name
        except KeyError:
            print("Campo 'holder' ou 'name' não encontrado na resposta.")
            return "Nome não encontrado"
