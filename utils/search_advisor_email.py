import json


class SearchAdvisorEmail:

    def __init__(self):
        pass

    def find_sgcge(self, account_number, account_data):
        for entry in account_data:
            if entry["account"] == account_number:
                return entry["sgCGE"]
        return None

    def find_email(self, sgcge, advisor_data):
        for advisor in advisor_data:
            if advisor["advisorCgeCode"] == sgcge:
                return advisor["email"]
        return None

    def get_advisor_email(self, account_number):
        with open("resources/data/account_advisors_data.json", "r") as f:
            account_data = json.load(f)

        with open("resources/data/advisors_data.json", "r") as f:
            advisor_data = json.load(f)

        sgcge = self.find_sgcge(account_number, account_data)
        if sgcge is None:
            return None

        email = self.find_email(sgcge, advisor_data)
        return email


# if __name__ == '__main__':
#     search_advisor_email = SearchAdvisorEmail()
#     account_number = '5870324'
#     advisor_email = search_advisor_email.get_advisor_email(account_number)
#     print(f'The advisor email for account {account_number} is {advisor_email}')
