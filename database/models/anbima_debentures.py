from sqlalchemy import Column, Integer, String, Float, Date
from .base import Base


class AnbimaDebentures(Base):
    __tablename__ = "anbima_debentures"

    id = Column(Integer, primary_key=True, autoincrement=True)

    codigo_ativo = Column(String, nullable=False)

    data_referencia = Column(Date, nullable=False)
    data_vencimento = Column(Date, nullable=False)

    desvio_padrao = Column(Float)
    duration = Column(Integer)
    percent_pu_par = Column(Float)
    percent_reune = Column(String)
    percentual_taxa = Column(String)
    pu = Column(Float)
    taxa_compra = Column(Float)
    taxa_indicativa = Column(Float)
    taxa_venda = Column(Float)
    val_max_intervalo = Column(Float)
    val_min_intervalo = Column(Float)

    emissor = Column(String, nullable=False)
    grupo = Column(String, nullable=False)

    def __repr__(self):
        return f'<AnbimaDebentures(codigo_ativo="{self.codigo_ativo}", data_referencia="{self.data_referencia}")>'
