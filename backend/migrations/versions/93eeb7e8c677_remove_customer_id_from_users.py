"""Remove customer_id from Users

Revision ID: 93eeb7e8c677
Revises: 873741ad5e9b
Create Date: 2025-07-13 22:32:42.305550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93eeb7e8c677'
down_revision = '873741ad5e9b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=False)
        batch_op.create_unique_constraint('uq_customers_user_id', ['user_id'])
        batch_op.create_foreign_key('fk_customers_user_id', 'Users', ['user_id'], ['user_id'])

    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.drop_column('customer_id')  # ✅ เหลือแค่นี้



def downgrade():
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customer_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key('fk_users_customer_id', 'Customers', ['customer_id'], ['customer_id'])

    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.drop_constraint('fk_customers_user_id', type_='foreignkey')
        batch_op.drop_constraint('uq_customers_user_id', type_='unique')
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)

    op.create_table('_alembic_tmp_Customers',
    sa.Column('customer_id', sa.INTEGER(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=50), nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=50), nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), nullable=False),
    sa.Column('phone_number', sa.VARCHAR(length=20), nullable=True),
    sa.Column('address', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['Users.user_id'], name='fk_customers_user_id'),
    sa.PrimaryKeyConstraint('customer_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('user_id', name='uq_customers_user_id')
    )
    # ### end Alembic commands ###
