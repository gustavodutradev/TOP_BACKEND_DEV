"""create anbima_debentures

Revision ID: e39f5588ca53
Revises: 5b6f2b464613
Create Date: 2024-11-21 21:15:26.175232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e39f5588ca53'
down_revision: Union[str, None] = '5b6f2b464613'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('anbima_debentures',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('codigo_ativo', sa.String(), nullable=False),
    sa.Column('data_referencia', sa.Date(), nullable=False),
    sa.Column('data_vencimento', sa.Date(), nullable=False),
    sa.Column('desvio_padrao', sa.Float(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('percent_pu_par', sa.Float(), nullable=True),
    sa.Column('percent_reune', sa.String(), nullable=True),
    sa.Column('percentual_taxa', sa.String(), nullable=True),
    sa.Column('pu', sa.Float(), nullable=True),
    sa.Column('taxa_compra', sa.Float(), nullable=True),
    sa.Column('taxa_indicativa', sa.Float(), nullable=True),
    sa.Column('taxa_venda', sa.Float(), nullable=True),
    sa.Column('val_max_intervalo', sa.Float(), nullable=True),
    sa.Column('val_min_intervalo', sa.Float(), nullable=True),
    sa.Column('emissor', sa.String(), nullable=False),
    sa.Column('grupo', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contas',
    sa.Column('account_number', sa.String(), nullable=False),
    sa.Column('type_fund', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('account_number')
    )
    op.create_index(op.f('ix_contas_account_number'), 'contas', ['account_number'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contas_account_number'), table_name='contas')
    op.drop_table('contas')
    op.drop_table('anbima_debentures')
    # ### end Alembic commands ###
