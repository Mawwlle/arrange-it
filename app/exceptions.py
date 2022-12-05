class DBPoolConnectException(Exception):
    """Raises when accessing to methods of pool without connection"""


class EntityDuplicateException(Exception):
    """Raises when entity is already exists in database"""
