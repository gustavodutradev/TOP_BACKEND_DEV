# import json


# class SearchAdvisorEmail:
#     def __init__(self):
#         pass

#     def find_sgcge_and_client_name(self, account_number, account_data):
#         """Busca o código CGE do assessor a partir do número da conta do cliente."""
#         for entry in account_data:
#             if entry["account"] == account_number:
#                 return entry["sgCGE"], entry["clientName"]
#         return None, None

#     def get_client_info(self, account_number):
#         """Obtém as informações do cliente e CGE do assessor, a partir do número da conta."""
#         with open("resources/data/account_advisors_data.json", "r") as f:
#             account_data = json.load(f)

#         client_info = self.find_sgcge_and_client_name(account_number, account_data)
#         if client_info is None:
#             return None, None

#         return client_info

#     def find_advisor_info(self, sgcge, advisor_data):
#         """Busca o e-mail e nome do assessor pelo código CGE."""
#         for advisor in advisor_data:
#             if advisor["advisorCgeCode"] == sgcge:
#                 return advisor["email"], advisor["advisorName"]
#         return None, None

#     def get_advisor_info(self, account_number):
#         """Obtém as informações do assessor a partir do número da conta."""
#         with open("resources/data/account_advisors_data.json", "r") as f:
#             account_data = json.load(f)

#         with open("resources/data/advisors_data.json", "r") as f:
#             advisor_data = json.load(f)

#         sgcge, client_name = self.find_sgcge_and_client_name(account_number, account_data)
#         if sgcge is None:
#             return None, None

#         return self.find_advisor_info(sgcge, advisor_data)

import json


class SearchAdvisorEmail:
    def __init__(self):
        self.account_data = self.load_json("resources/data/account_advisors_data.json")
        self.advisor_data = self.load_json("resources/data/advisors_data.json")

    @staticmethod
    def load_json(filepath):
        """Carrega dados de um arquivo JSON e lida com possíveis erros."""
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo {filepath} não encontrado.")
            return []
        except json.JSONDecodeError:
            print(f"Erro: Falha ao decodificar o arquivo {filepath}.")
            return []

    def find_sgcge_by_account(self, account_number):
        """Busca o código CGE do assessor a partir do número da conta do cliente."""
        for entry in self.account_data:
            if entry.get("account") == account_number:
                return entry.get("sgCGE")
        return None

    def find_client_name_by_account(self, account_number):
        """Busca o nome do cliente a partir do número da conta."""
        for entry in self.account_data:
            if entry.get("account") == account_number:
                return entry.get("clientName")
        return None

    def find_advisor_email_and_name(self, sgcge):
        """Busca o e-mail e nome do assessor pelo código CGE."""
        for advisor in self.advisor_data:
            if advisor.get("advisorCgeCode") == sgcge:
                return advisor.get("email"), advisor.get("advisorName")
        return None, None

    def get_client_and_advisor_info(self, account_number):
        """Obtém informações do cliente e do assessor a partir do número da conta."""
        sgcge = self.find_sgcge_by_account(account_number)
        client_name = self.find_client_name_by_account(account_number)

        if sgcge is None:
            print(f"Código CGE não encontrado para a conta {account_number}.")
            return client_name, None, None

        email, advisor_name = self.find_advisor_email_and_name(sgcge)

        if email is None or advisor_name is None:
            print(f"Assessor com CGE {sgcge} não encontrado.")
            return client_name, None, None

        return client_name, advisor_name, email, sgcge
