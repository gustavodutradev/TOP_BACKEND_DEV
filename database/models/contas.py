from sqlalchemy import Column, String, Boolean
from .base import Base

class Conta(Base):
    __tablename__ = "contas"

    account_number = Column(String, primary_key=True, index=True)
    type_fund = Column(Boolean)

    def __repr__(self):
        return (
            f"<Conta(account_number={self.account_number}, type_fund={self.type_fund})>"
        )
