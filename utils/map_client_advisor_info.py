import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvisorLookup:
    def __init__(self):
        # Carrega os dados de contas e assessores a partir de arquivos JSON
        self.account_data = self.load_json("resources/data/account_advisors_data.json")
        self.advisor_data = self.load_json("resources/data/advisors_data.json")

        # Verifica se os dados foram carregados corretamente
        if self.account_data and self.advisor_data:
            logger.info("Dados de contas e assessores carregados com sucesso.")
            logger.info(f"Total de contas carregadas: {len(self.account_data)}")
            logger.info(f"Total de assessores carregados: {len(self.advisor_data)}")
        else:
            logger.error("Erro ao carregar os dados de contas e assessores.")

    @staticmethod
    def load_json(filepath):
        """Carrega dados de um arquivo JSON e lida com possíveis erros."""
        try:
            with open(filepath, "r", encoding='utf-8') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            logger.error(f"Erro: Arquivo {filepath} não encontrado.")
            return []
        except json.JSONDecodeError:
            logger.error(f"Erro: Falha ao decodificar o arquivo {filepath}.")
            return []

    def get_advisor_info(self, account_number):
        """
        Dado um número de conta, retorna as informações do assessor responsável.
        
        Parameters:
        account_number (str/int): Número da conta a ser pesquisada.
        
        Returns:
        dict: Dicionário contendo as informações do assessor (nome, email).
        """
        # Converte o número da conta para string para garantir a comparação correta
        account_number = str(account_number)
        
        try:
            logger.debug(f"Procurando conta: {account_number}")
            
            # Procura os dados do cliente com o número de conta fornecido
            client_data = next((data for data in self.account_data if str(data['account']) == account_number), None)
            
            if client_data:
                logger.info(f"Dados do cliente encontrados")
                # Procura os dados do assessor correspondente
                advisor_data = next((data for data in self.advisor_data if data['advisorCgeCode'] == client_data['sgCGE']), None)
                
                if advisor_data:
                    logger.info(f"Dados do assessor encontrados")
                    return {
                        'advisorName': advisor_data['advisorName'],
                        'email': advisor_data['email']
                    }
                else:
                    logger.error(f"Não foi possível encontrar os dados do assessor com o código CGE {client_data['sgCGE']}")
            else:
                logger.error(f"Não foi possível encontrar os dados do cliente com o número de conta {account_number}")
        except Exception as e:
            logger.error(f"Erro ao processar os dados: {e}")
        
        return None