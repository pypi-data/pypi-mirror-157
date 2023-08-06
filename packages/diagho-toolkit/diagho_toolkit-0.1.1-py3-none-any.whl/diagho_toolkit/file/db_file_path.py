# WARNING !
# This may be change drasticaly, move, and/or delete soon

import os

from typing import Tuple, List

from django.conf import settings


def get_db_list() -> List[str]:
    """return list of all resgistered database"""
    return os.listdir(str(settings.BIODB_ROOT) + "/data/")


class DbDoesNotExistError(Exception):
    def __init__(self, Database):
        super().__init__("Database {0} Does not exist".format(Database))


def get_versions(db: str) -> Tuple[Tuple[str, str]]:
    """return tuple of tuples of all version of a db with it corresponding path"""

    if not isinstance(db, str):
        raise ValueError("database name must be <str> not {0}".format(type(db)))

    if db not in get_db_list():
        raise DbDoesNotExistError(db)

    db_path = "/".join([str(settings.BIODB_ROOT), "data", db])

    return tuple(
        ("/".join([db_path, version]), version) for version in os.listdir(db_path)
    )


def get_file_path(version_path: str) -> Tuple[str]:
    """return tuple of the path of each file for a db version"""
    return tuple(
        ("/".join([version_path, filename]) for filename in os.listdir(version_path))
    )
