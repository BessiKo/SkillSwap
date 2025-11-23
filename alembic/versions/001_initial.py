"""Initial migration - users, profiles, badges

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('phone', sa.String(20), unique=True, nullable=False, index=True),
        sa.Column('role', sa.Enum('student', 'admin', name='userrole'), default='student', nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # User profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('first_name', sa.String(100), default=''),
        sa.Column('last_name', sa.String(100), default=''),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('bio', sa.Text(), default=''),
        sa.Column('university', sa.String(200), default=''),
        sa.Column('faculty', sa.String(200), default=''),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Float(), default=0.0),
        sa.Column('total_ratings', sa.Integer(), default=0),
        sa.Column('exchanges_completed', sa.Integer(), default=0),
        sa.Column('reviews_received', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Badges table
    op.create_table(
        'badges',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('type', sa.Enum('newcomer', 'first_exchange', 'popular', 'top_rated', 'mentor', 'expert', 
                                   name='badgetype'), unique=True, nullable=False),
        sa.Column('description', sa.String(200)),
        sa.Column('icon', sa.String(50)),
    )

    # User badges association table
    op.create_table(
        'user_badges',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('badge_id', sa.Integer(), sa.ForeignKey('badges.id'), primary_key=True),
        sa.Column('awarded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade() -> None:
    op.drop_table('user_badges')
    op.drop_table('badges')
    op.drop_table('user_profiles')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS badgetype')