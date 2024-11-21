from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Conta(Base):
    __tablename__ = "contas"

    account_number = Column(String, primary_key=True, index=True)
    type_fund = Column(Boolean)

    def __repr__(self):
        return (
            f"<Conta(account_number={self.account_number}, type_fund={self.type_fund})>"
        )
