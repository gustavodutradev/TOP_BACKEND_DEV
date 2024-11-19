import json
import requests
from core.services.config_service import ConfigService
import logging
import pandas as pd
import io  # Adicione esta importação para usar BytesIO

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

            # Convertendo os dados JSON para um DataFrame do pandas
            df = pd.json_normalize(response_data)

            # Usando um buffer de memória para salvar o Excel
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')  # Especifica o engine para criar o Excel

            # Movendo o cursor do buffer para o início
            excel_buffer.seek(0)

            # Retornando o conteúdo do Excel em bytes
            return excel_buffer.getvalue()

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return {"error": str(e)}
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta.")
            return {"error": "Erro ao decodificar a resposta da API."}
