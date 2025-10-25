"""Initial migration

Revision ID: 665a6b94cad5
Revises: dcc40c5c7692
Create Date: 2025-10-23 13:10:27.164975

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '665a6b94cad5'
down_revision = 'dcc40c5c7692'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create file_uploads table
    op.create_table(
        'file_uploads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create cleaning_history table
    op.create_table(
        'cleaning_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_id', sa.Integer(), sa.ForeignKey('file_uploads.id')),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('cleaned_file_path', sa.String(), nullable=True),
        sa.Column('cleaning_steps', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('cleaning_history')
    op.drop_table('file_uploads')
    op.drop_table('users')
