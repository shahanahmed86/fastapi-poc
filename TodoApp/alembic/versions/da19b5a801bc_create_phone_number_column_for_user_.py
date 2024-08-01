"""Create phone number column for user table

Revision ID: da19b5a801bc
Revises: 
Create Date: 2024-08-01 17:48:05.836060

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "da19b5a801bc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(15), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "phone_number")
