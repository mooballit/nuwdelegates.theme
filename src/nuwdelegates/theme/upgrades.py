from migrate.changeset.schema import rename_table, alter_column
from nuw.types import Base
from sqlalchemy import Integer, Column, String, Boolean
from sqlalchemy import PickleType
from sqlalchemy import MetaData
from z3c.saconfig import named_scoped_session
import nuw.types.setuphandlers as setuphandlers
from nuwdelegates.theme.member_list.tool import MemberListColumnConfig


Session = named_scoped_session("nuw.types")


def upgrade_1_to_2(context):
    session = Session()
    Base.metadata.bind = session.bind

    MemberListColumnConfig.__table__.create_column(Column('column_config', PickleType))
