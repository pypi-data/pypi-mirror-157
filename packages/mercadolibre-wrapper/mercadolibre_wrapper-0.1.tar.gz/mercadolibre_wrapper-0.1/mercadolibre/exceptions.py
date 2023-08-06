"""Exceptions classes"""


class BaseError(Exception):
    pass


class InvalidSite(BaseError):
    pass


class InvalidClient(BaseError):
    pass


class ResourceNotFount(BaseError):
    pass


class ItemNotFount(BaseError):
    pass


class Forbidden(BaseError):
    pass
