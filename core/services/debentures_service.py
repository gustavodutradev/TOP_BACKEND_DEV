import json
import requests
from core.services.config_service import ConfigService
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import AnbimaDebentures


class AnbimaDebenturesService:
    def __init__(self):
        self.config_service = ConfigService()

    def get_anbima_debentures(self, db: Session, reference_date):
        endpoint = "/iaas-debenture/api/v1/debenture"
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

            # Verifica se a resposta JSON é válida
            if response_data is None or not isinstance(response_data, (list, dict)):
                print("Resposta JSON é nula ou inválida.")
                return {"error": "Nenhum dado retornado."}

            # Processa as debêntures e salva no banco de dados
            if isinstance(response_data, list):
                self.save_anbima_debentures(db, response_data)
            elif isinstance(response_data, dict) and "debentures" in response_data:
                self.save_anbima_debentures(db, response_data["debentures"])

            # Retorna a resposta correta
            return response_data

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return {"error": str(e)}
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta.")
            return {"error": "Erro ao decodificar a resposta da API."}

    def save_anbima_debentures(self, session: Session, debentures_data_list):
        for debenture_data in debentures_data_list:
            if "codigo_ativo" not in debenture_data:
                print("Campo 'codigo_ativo' não encontrado nos dados da debênture.")
                continue

            existing_debenture = (
                session.query(AnbimaDebentures)
                .filter_by(codigo_ativo=debenture_data["codigo_ativo"])
                .first()
            )
            if not existing_debenture:
                # Cria uma nova instância da debênture
                new_debenture = AnbimaDebentures(**debenture_data)
                session.add(new_debenture)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print(
                "Erro de integridade: houve tentativa de inserir uma debênture duplicada."
            )
