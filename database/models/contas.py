from sqlalchemy import Column, String, Boolean
from .base import Base

class Conta(Base):
    __tablename__ = "contas"

    accountNumber = Column(String, primary_key=True, index=True)
    typeFund = Column(Boolean)

    def __repr__(self):
        return (
            f"<Conta(account_number={self.account_number}, type_fund={self.type_fund})>"
        )
