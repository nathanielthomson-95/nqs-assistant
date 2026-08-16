"""add hnsw index on chunk embeddings

Revision ID: d9dd08fae640
Revises: ea63b2438122
Create Date: 2026-08-16 19:00:21.474233

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9dd08fae640'
down_revision: Union[str, Sequence[str], None] = 'ea63b2438122'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass



def upgrade() -> None:
    op.execute(
        "CREATE INDEX chunks_embedding_hnsw "
        "ON chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS chunks_embedding_hnsw")
