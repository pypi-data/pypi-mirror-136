# PyStark - Python add-on extension to Pyrogram
# Copyright (C) 2021-2022 Stark Bots <https://github.com/StarkBotsIndustries>
#
# This file is part of PyStark.
#
# PyStark is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyStark is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyStark. If not, see <https://www.gnu.org/licenses/>.


import traceback
import sqlalchemy
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from ..config import DATABASE_URL
from pystark import Stark


if not DATABASE_URL:
    Stark.log('No DATABASE_URL defined. Exiting...', "critical")
    raise SystemExit


def start() -> scoped_session:
    engine = create_engine(DATABASE_URL)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


Base = declarative_base()
# Type-Hinting is wrong here, but a temporary way to get Hints for Session object
Session: sqlalchemy.orm.Session = start()


async def get_db(table_name: str, primary_key, key: str = None):
    """Get data from postgres database using table name as string.
    Returns dict if key_name is not passed.

    Parameters:
        table_name (``str``):
            The table name to query on.

        primary_key:
            The value of a primary_key to query the table.

        key (``str``, *optional*):
            If passed, only value for the specified key is returned.
    """
    tables_dict = await _tables_dict()
    table_exists = await _table_exists(table_name)
    if not table_exists:
        return
    table = tables_dict[table_name]
    query = Session.query(table).get(primary_key)
    if key:
        return query[key]
    return _class_vars(query)


async def set_db(table_name: str, primary_key, key: str, value) -> bool:
    """Set data in postgres database using table name as string.

    Parameters:
        table_name (``str``):
            The table name to query on.

        primary_key:
            The value of a primary_key to query the table.

        key (``str``):
            The key name to set value in.

        value:
            The value for the key.

    Returns:
        ``bool``: True on success
    """
    tables_dict = await _tables_dict()
    table_exists = await _table_exists(table_name)
    if not table_exists:
        return False
    table = tables_dict[table_name]
    try:
        query = Session.query(table).get(primary_key)
        setattr(query, key, value)
        Session.commit()
        return True
    except Exception as e:
        Session.rollback()
        Stark.log(str(e), "critical")
        print(traceback.format_exc())


async def count_db(table_name: str) -> Optional[int]:
    """Get number of rows in postgres table.

    Parameters:
        table_name:
            The table name to query on.
    """
    tables_dict = await _tables_dict()
    table_exists = await _table_exists(table_name)
    if not table_exists:
        return
    table = tables_dict[table_name]
    count = Session.query(table).count()
    return count


async def all_db(table_name: str) -> Optional[list]:
    """Get all rows in postgres table.

    Parameters:
        table_name (``str``):
            The table name to query on.
    """
    tables_dict = await _tables_dict()
    table_exists = await _table_exists(table_name)
    if not table_exists:
        return
    table = tables_dict[table_name]
    all_ = Session.query(table).all()
    Session.close()
    return [_class_vars(d) for d in all_]


async def delete_db(table_name: str, primary_key) -> None:
    """Delete row in postgres database using table name as string.

    Parameters:
        table_name (``str``):
            The table name to query on.

        primary_key:
            The value of a primary_key to query the table.
    """
    tables_dict = await _tables_dict()
    table_exists = await _table_exists(table_name)
    if not table_exists:
        return
    table = tables_dict[table_name]
    try:
        query = Session.query(table).get(primary_key)
        Session.delete(query)
        Session.commit()
    except Exception as e:
        Session.rollback()
        Stark.log(str(e), "critical")
        print(traceback.format_exc())


# Private Functions
async def _tables_dict() -> dict:
    """Returns all {tablename: table}"""
    return {table.__tablename__: table for table in Base.__subclasses__()}


async def _table_exists(table_name: str) -> bool:
    """Returns True if table exists else False"""
    tables_dict = await _tables_dict()
    if table_name in tables_dict:
        return True
    else:
        return False


def _class_vars(class_obj) -> dict:
    v = vars(class_obj)
    return {key: v[key] for key in v if key != "_sa_instance_state"}
