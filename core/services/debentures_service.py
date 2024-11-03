from core.services.config_service import ConfigService
import requests
import json


class DebenturesService:
    def __init__(self):
        self.config_service = ConfigService()

    def get_anbima_debentures(self, reference_date):
        endpoint = f"/iaas-debenture/api/v1/debenture"
        url = f"{self.config_service.base_url}{endpoint}"

        params = {"referenceDate": reference_date}

        print(url)

        try:
            headers = self.config_service.get_headers()

            response = requests.get(url, headers=headers, params=params)

            # Logando status code e response text
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            # Verifica se a resposta não é 200
            if response.status_code != 200:
                print(
                    f"Erro ao acessar debentures: {response.status_code} - {response.text}"
                )
                return {"error": "Falha ao acessar o endpoint."}

            # Tentando decodificar a resposta JSON
            response_data = response.json()

            # Verifica se a resposta JSON é uma lista ou dicionário válido
            if not response_data or not isinstance(response_data, (list, dict)):
                print("Resposta JSON é nula ou inválida.")
                return {"error": "Nenhum dado retornado."}

            # Retorna a resposta correta (independentemente se é lista ou dict)
            return response_data

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return {"error": str(e)}

        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta.")
            return {"error": "Erro ao decodificar a resposta da API."}
