class DatabaseNotInitializedException(Exception):
    """Вызывается когда база данных не инициализировалась"""


class EntityDuplicateException(Exception):
    """Raises when entity is already exists in database"""
