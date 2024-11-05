import json


class SearchAdvisorEmail:
    def __init__(self):
        pass

    def find_sgcge_and_client_name(self, account_number, account_data):
        """Busca o código CGE do assessor a partir do número da conta do cliente."""
        for entry in account_data:
            if entry["account"] == account_number:
                return entry["sgCGE"], entry["clientName"]
        return None, None

    def get_client_info(self, account_number):
        """Obtém as informações do cliente e CGE do assessor, a partir do número da conta."""
        with open("resources/data/account_advisors_data.json", "r") as f:
            account_data = json.load(f)

        client_info = self.find_sgcge_and_client_name(account_number, account_data)
        if client_info is None:
            return None, None

        return client_info

    def find_advisor_info(self, sgcge, advisor_data):
        """Busca o e-mail e nome do assessor pelo código CGE."""
        for advisor in advisor_data:
            if advisor["advisorCgeCode"] == sgcge:
                return advisor["email"], advisor["advisorName"]
        return None, None

    def get_advisor_info(self, account_number):
        """Obtém as informações do assessor a partir do número da conta."""
        with open("resources/data/account_advisors_data.json", "r") as f:
            account_data = json.load(f)

        with open("resources/data/advisors_data.json", "r") as f:
            advisor_data = json.load(f)

        sgcge, _ = self.find_sgcge_and_client_name(account_number, account_data)
        if sgcge is None:
            return None, None

        return self.find_advisor_info(sgcge, advisor_data)
