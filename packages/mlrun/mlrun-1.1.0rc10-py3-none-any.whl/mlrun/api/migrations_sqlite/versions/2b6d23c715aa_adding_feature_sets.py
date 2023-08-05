"""Adding feature sets

Revision ID: 2b6d23c715aa
Revises: b68e8e897a28
Create Date: 2020-11-05 01:42:53.395810

"""
import sqlalchemy as sa
from alembic import op

from mlrun.api.utils.db.sql_collation import SQLCollationUtil

# revision identifiers, used by Alembic.
revision = "2b6d23c715aa"
down_revision = "b68e8e897a28"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "feature_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "name",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.Column(
            "project",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.Column("created", sa.TIMESTAMP(), nullable=True),
        sa.Column("updated", sa.TIMESTAMP(), nullable=True),
        sa.Column(
            "state",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.Column(
            "uid", sa.String(255, collation=SQLCollationUtil.collation()), nullable=True
        ),
        sa.Column("status", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "project", "uid", name="_feature_set_uc"),
    )
    op.create_table(
        "entities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("feature_set_id", sa.Integer(), nullable=True),
        sa.Column(
            "name",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.Column(
            "value_type",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["feature_set_id"],
            ["feature_sets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "feature_sets_labels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "name",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.Column(
            "value",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.Column("parent", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent"],
            ["feature_sets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "parent", name="_feature_sets_labels_uc"),
    )
    op.create_table(
        "feature_sets_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "project",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.Column(
            "name",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.Column("obj_id", sa.Integer(), nullable=True),
        sa.Column(
            "obj_name",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["obj_id"],
            ["feature_sets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["obj_name"],
            ["feature_sets.name"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project", "name", "obj_name", name="_feature_sets_tags_uc"
        ),
    )
    op.create_table(
        "features",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("feature_set_id", sa.Integer(), nullable=True),
        sa.Column(
            "name",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.Column(
            "value_type",
            sa.String(255, collation=SQLCollationUtil.collation()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["feature_set_id"],
            ["feature_sets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("features")
    op.drop_table("feature_sets_tags")
    op.drop_table("feature_sets_labels")
    op.drop_table("entities")
    op.drop_table("feature_sets")
    # ### end Alembic commands ###
