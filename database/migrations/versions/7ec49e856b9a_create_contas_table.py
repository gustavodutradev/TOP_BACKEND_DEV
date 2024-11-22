"""create contas table

Revision ID: 7ec49e856b9a
Revises: 
Create Date: 2024-11-21 11:14:36.774968

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7ec49e856b9a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "contas",
        sa.Column("account_number", sa.String(), nullable=False),
        sa.Column("type_fund", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("account_number"),
    )
    op.create_index(
        op.f("ix_contas_account_number"), "contas", ["account_number"], unique=False
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("contas")
