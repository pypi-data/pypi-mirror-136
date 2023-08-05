"""First revision

This revision creates all the initial tables on the database.

Revision ID: 713b76b25d40
Revises: 
Create Date: 2021-11-12 05:12:50.740928
"""
import sqlalchemy as sa
import sqlalchemy.exc
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '713b76b25d40'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('webhook', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'groups',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crystal', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id', 'crystal')
    )
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crystal', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id', 'crystal')
    )
    op.create_table(
        'achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('alloy', sa.Enum('BRONZE', 'SILVER', 'GOLD', name='alloy'), nullable=False),
        sa.Column('secret', sa.Boolean(), nullable=False),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('repeatable', sa.Boolean(), nullable=False),
        sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'unlocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('unlocks')
    op.drop_table('achievements')
    op.drop_table('users')
    op.drop_table('groups')
    op.drop_table('applications')

    try:
        op.execute("DROP TYPE alloy")
    except sqlalchemy.exc.ProgrammingError:
        pass
