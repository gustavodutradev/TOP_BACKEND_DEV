"""initial migration

Revision ID: aefbed9fc41b
Revises: 
Create Date: 2024-11-21 21:26:40.861243

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aefbed9fc41b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "anbima_debentures",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo_ativo", sa.String(), nullable=False),
        sa.Column("data_referencia", sa.Date(), nullable=False),
        sa.Column("data_vencimento", sa.Date(), nullable=False),
        sa.Column("desvio_padrao", sa.Float(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("percent_pu_par", sa.Float(), nullable=True),
        sa.Column("percent_reune", sa.String(), nullable=True),
        sa.Column("percentual_taxa", sa.String(), nullable=True),
        sa.Column("pu", sa.Float(), nullable=True),
        sa.Column("taxa_compra", sa.Float(), nullable=True),
        sa.Column("taxa_indicativa", sa.Float(), nullable=True),
        sa.Column("taxa_venda", sa.Float(), nullable=True),
        sa.Column("val_max_intervalo", sa.Float(), nullable=True),
        sa.Column("val_min_intervalo", sa.Float(), nullable=True),
        sa.Column("emissor", sa.String(), nullable=False),
        sa.Column("grupo", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "contas",
        sa.Column("accountNumber", sa.String(), nullable=False),
        sa.Column("typeFund", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("accountNumber"),
    )
    op.create_index(
        op.f("ix_contas_accountNumber"), "contas", ["accountNumber"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_contas_accountNumber"), table_name="contas")
    op.drop_table("contas")
    op.drop_table("anbima_debentures")
    # ### end Alembic commands ###
