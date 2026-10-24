"""initial tenant, job, event, graph, case and audit schema"""
from alembic import op

revision = "0001_initial_platform"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    from chainbreaker.storage.models import Base
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    from chainbreaker.storage.models import Base
    Base.metadata.drop_all(bind=op.get_bind())
