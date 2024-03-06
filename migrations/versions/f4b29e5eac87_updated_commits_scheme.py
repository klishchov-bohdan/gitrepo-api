"""updated commits scheme

Revision ID: f4b29e5eac87
Revises:
Create Date: 2024-03-04 18:56:30.024785

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f4b29e5eac87'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('author',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('time_created', sa.TIMESTAMP(), server_default=sa.text(
                        'CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('time_updated', sa.TIMESTAMP(), server_default=sa.text(
                        'CURRENT_TIMESTAMP'), nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_author')),
                    sa.UniqueConstraint('name', name=op.f('uq_author_name '))
                    )
    op.create_index(op.f('ix_author_id '), 'author', ['id'], unique=True)
    op.create_table('repository',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('repo', sa.String(), nullable=False),
                    sa.Column('owner', sa.String(), nullable=False),
                    sa.Column('position_cur', sa.Integer(), nullable=False),
                    sa.Column('position_prev', sa.Integer(), nullable=False),
                    sa.Column('stars', sa.Integer(), nullable=False),
                    sa.Column('watchers', sa.Integer(), nullable=False),
                    sa.Column('forks', sa.Integer(), nullable=False),
                    sa.Column('open_issues', sa.Integer(), nullable=False),
                    sa.Column('language', sa.String(), nullable=False),
                    sa.Column('time_created', sa.TIMESTAMP(), server_default=sa.text(
                        'CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('time_updated', sa.TIMESTAMP(), server_default=sa.text(
                        'CURRENT_TIMESTAMP'), nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_repository')),
                    sa.UniqueConstraint('repo', name=op.f('uq_repository_repo '))
                    )
    op.create_index(op.f('ix_repository_id '), 'repository', ['id'], unique=True)
    op.create_table('repository_author',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('repository_id', sa.Integer(), nullable=False),
                    sa.Column('author_id', sa.Integer(), nullable=False),
                    sa.Column('pushed_at', sa.TIMESTAMP(), nullable=False),
                    sa.Column('time_created', sa.TIMESTAMP(), server_default=sa.text(
                        'CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('time_updated', sa.TIMESTAMP(), server_default=sa.text(
                        'CURRENT_TIMESTAMP'), nullable=False),
                    sa.ForeignKeyConstraint(['author_id'], ['author.id'], name=op.f(
                        'fk_repository_author_author_id_author'), ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], name=op.f(
                        'fk_repository_author_repository_id_repository'), ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_repository_author'))
                    )
    op.create_index(op.f('ix_repository_author_id '), 'repository_author', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_repository_author_id '), table_name='repository_author')
    op.drop_table('repository_author')
    op.drop_index(op.f('ix_repository_id '), table_name='repository')
    op.drop_table('repository')
    op.drop_index(op.f('ix_author_id '), table_name='author')
    op.drop_table('author')
    # ### end Alembic commands ###
