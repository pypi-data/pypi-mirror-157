"""Response object."""


class Response:
    def __init__(self, response):
        self._response = response
        self.url = response.url
        self.status_code = response.status_code
        self.data = response.json()

    def __repr__(self):
        return '<{} [{}]>'.format(
            self.__class__.__name__, self.status_code)

    def get_data(self):
        """Return data from json response."""
        return self.data['results']
