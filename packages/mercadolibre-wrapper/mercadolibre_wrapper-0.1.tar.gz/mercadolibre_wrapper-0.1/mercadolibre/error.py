"""Error object."""
#
from .exceptions import ItemNotFount, ResourceNotFount, Forbidden

# TODO


class Error(Exception):
    """_summary_

    Args:
        Exception (_type_): _description_
    """

    def __init__(self, error):
        if isinstance(error, str):
            super().__init__(error)
            return

        self.http_status = None
        self.json_body = None
        self.code = None

        try:
            res = error.response
        except AttributeError:
            res = None
        if res is not None:
            try:
                self.http_status = res.status_code
                self.json_body = res.json()

                if self.json_body['error'] == 'resource not found':
                    raise ResourceNotFount(error)

                self.code = self.json_body['status']

                message = self.json_body['message']
            except (KeyError, ValueError):
                message = str(error)

            if self.json_body['error'] == 'not_found':
                raise ItemNotFount(error) from None

            if self.json_body['error'] == 'forbidden':
                raise Forbidden(error) from None

        else:
            message = str(error)

        super().__init__(message)
