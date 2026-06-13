"""initial migration"""

from alembic import op
import sqlalchemy as sa
import sys, os
sys.path.insert(0, os.path.abspath('.'))

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    from src.db import engine, Base
    Base.metadata.create_all(bind=engine)

def downgrade():
    from src.db import engine, Base
    Base.metadata.drop_all(bind=engine)
