"""create a new table

Revision ID: c751a19c458e
Revises: 
Create Date: 2023-06-13 12:38:31.882003

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import String, Integer, Column,Boolean
from sqlalchemy.sql import table,column


# revision identifiers, used by Alembic.
revision = 'c751a19c458e'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'Books',
        sa.Column('book_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('summary', sa.Text, nullable=False),
        sa.Column('isbn', sa.String(255), nullable=False),
        sa.Column('author', sa.String(255), nullable=False),
    )
    op.create_table(
        'Authors',
        sa.Column('author_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
    )
    op.create_table(
        'Users',
        sa.Column('username', sa.String(255), primary_key=True),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('isAdmin', sa.Boolean, nullable=False),

    )
    data_upgrades_authortable()
    data_upgrades_booktable()
    data_upgrades_usertable()
    

def data_upgrades_usertable():
        my_table = table('Users',
            column('username', String),
            column('password', String),
             column('isAdmin', Boolean)
        )

        op.bulk_insert(my_table,
            [
                {'username': 'string',
                 'password':'string',
                 "isAdmin":True},
            ]
        )
    
def data_upgrades_authortable():
        my_table = table('Authors',
            column('author_id', Integer),
            column('name', String),
        )

        op.bulk_insert(my_table,
            [
                {
                 'name':'Maria'},
                 {
                 'name':'Jean'},
            ]
        )
def data_upgrades_booktable():
        my_table = table('Books',
            column('book_id', Integer),
            column('title', String),
            column('summary', String),
            column('isbn', String),
            column('author', String),
        )

        op.bulk_insert(my_table,
            [
                {
                 'title':'Oceans',
                 'summary':'description1',
                 'isbn':'978-1-945209-05-5',
                 'author':'Jean',
                 },
                 {
                 'title':'Deserts',
                 'summary':'description2',
                 'isbn':'978-1-945329-05-5',
                 'author':'Maria',
                 },
            ]
        )

def downgrade():
    pass
